import chromadb
from typing import List
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.config import Settings
from app.models import ChatMessage



class RagService:
    def __init__(self):
        self.cloud_client = chromadb.CloudClient(
            api_key=Settings.CHROMA_API_KEY, tenant=Settings.CHROMA_TENANT,database=Settings.CHROMA_DATABASE
        )

        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            google_api_key=Settings.GOOGLE_API_KEY,
            temperature=0,
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", google_api_key=Settings.GOOGLE_API_KEY
        )
        self.vectorstore = Chroma(
            client=self.cloud_client,
            collection_name='rag_collection',
            embedding_function=self.embeddings,
        )
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        self.standard_rag_chain = self._build_standard_rag_chain()
        self.conversational_rag_chain = self._build_conversational_rag_chain()
        
        
    def _build_standard_rag_chain(self):
        qa_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful assistant for question-answering task."
                "Use only the provided context to answer the user's question."
                "If the answer is not present in the context, say you don't know.\n\n"
                "Context:\n{context}\n\n"
            ),
            ("human", "{input}")
        ])
        combine_docs_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=qa_prompt,
        )
        return create_retrieval_chain(
            retriever=self.retriever,
            combine_docs_chain=combine_docs_chain,
        )
    def _build_conversational_rag_chain(self):
        qa_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful assistant for question-answering task. Use only the provided context to answer the user's question. If the answer is not present in the context, say you don't know.\n\n"
                "Context:\n{context}\n\n"
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        return create_stuff_documents_chain(
            llm=self.llm,
            prompt=qa_prompt,
        )
    
    @staticmethod
    def format_chat_history(chat_history: List):
        formatted = []
        for msg in chat_history:
            role = msg.role
            content = msg.content
            if role == "human":
                formatted.append(HumanMessage(content=content))
            else:
                formatted.append(AIMessage(content=content))
        return formatted
    
    @staticmethod
    def extract_sources(context_docs):
        sources = []
        for doc in context_docs:
            source = doc.metadata.get("source", "unknown")
            if source not in sources:
                sources.append(source)
        return sources
    
    def health(self):
        count = self.vectorstore._collection.count()
        return {
            "status": "ready",
            "vectorstore": True,
            "chroma_cloud": True,
            "collection_name": "rag_collection",
            "document_count": count,
        }
    
    def ask(self, question: str):
        result = self.standard_rag_chain.invoke({"input": question})
        context_docs = result.get("context", [])

        return {
            "mode":"standard_rag",
            "question": question,
            "answer": result.get("answer", "No answer generated."),
            "sources": self.extract_sources(context_docs),
            "context_count": len(context_docs),
        }
    
    def chat(self, question: str, chat_history: List[ChatMessage]):
        formatted_history = self.format_chat_history(chat_history)
        try:
            if formatted_history:
                contextualize_prompt = ChatPromptTemplate.from_messages([
                    (
                        "system",
                        """Given the chat history and latest user question, rewrite the
                        question into a standalone question that can be understood
                        without the chat history. Do not anwer the question."""
                    ),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}")
                ])
                chain = contextualize_prompt | self.llm
                rewritten = chain.invoke({
                    "input": question,
                    "chat_history": formatted_history,
                })
                standalone_question = rewritten.content
                print("Standalone question generated:", standalone_question)
            else:
                standalone_question = question

            context_docs = self.retriever.invoke(standalone_question)
            print(f"Retrieved {len(context_docs)} context documents.")
            answer = self.conversational_rag_chain.invoke({
                "input": question,
                "context": context_docs,
                "chat_history": formatted_history,
            })
            return {
                "mode":"conversational_rag",
                "question": question,
                "answer": answer,
                "sources": self.extract_sources(context_docs),
                "context_count": len(context_docs),
                "chat_history_used": len(chat_history),
            }
        except Exception as e:
            print("Error during conversational RAG processing:", str(e))
            raise 

            
        
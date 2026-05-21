from pathlib import Path
import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import Settings

def load_documents(data_dir: str= "data"):
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory '{data_dir}' not found.")
    docs = []
    for file_path in data_path.glob("*.txt"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        docs.extend(loader.load())
    if not docs:
        raise ValueError(f"No text files found in '{data_dir}'.")
    return docs

def main():
    print("Loading documents...")
    documents = load_documents("data")
    print(f"Loaded {len(documents)} documents.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    cloud_client = chromadb.CloudClient(
        api_key=Settings.CHROMA_API_KEY, tenant=Settings.CHROMA_TENANT,database=Settings.CHROMA_DATABASE
    )
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", google_api_key=Settings.GOOGLE_API_KEY
    )
    vectorstore = Chroma(
        client=cloud_client,
        collection_name='rag_collection',
        embedding_function=embeddings,
    )
    vectorstore.add_documents(chunks)
    count = vectorstore._collection.count()
    print(f"Ingestion complete. Total documents/chunks in collection: {count}")

if __name__ == "__main__":
    main()

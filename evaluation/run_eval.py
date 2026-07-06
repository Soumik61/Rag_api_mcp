import os
import requests
from dotenv import load_dotenv
from test_evaluations import test_data
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv("../.env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

RAG_API_URL = "http://20.81.100.218"  # apna AKS external IP daalo

def ask_rag_api(question):
    response = requests.post(f"{RAG_API_URL}/ask", json={"question": question})
    return response.json()

results = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

for item in test_data:
    print(f"Processing: {item['question']}")
    response = ask_rag_api(item["question"])
    
    results["question"].append(item["question"])
    results["answer"].append(response.get("answer", ""))
    results["contexts"].append(response.get("sources", [response.get("answer", "")]))
    results["ground_truth"].append(item["ground_truth"])

eval_dataset = Dataset.from_dict(results)

evaluator_llm = LangchainLLMWrapper(
    ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
)
evaluator_embeddings = LangchainEmbeddingsWrapper(
    GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=GOOGLE_API_KEY)
)

print("\nRunning RAGAS evaluation...")
score = evaluate(
    eval_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=evaluator_llm,
    embeddings=evaluator_embeddings,
)

print(score)
df = score.to_pandas()
df.to_csv("results.csv", index=False)
print("Saved to evaluation/results.csv")
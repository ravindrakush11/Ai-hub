from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings

# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters import CharacterTextSplitter

# from langchain.llms import OpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import requests

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

# Step 1: Load and index documents
loader = TextLoader("knowledge_base/faq.txt")
docs = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(docs)

# Step 2: Create embeddings and vector store
embedding = HuggingFaceEmbeddings(
        model_name = r"D:\AI\Embedding_models\models--BAAI--bge-small-en-v1.5\snapshots\5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
        encode_kwargs={"normalize_embeddings": True},  # Recommended for cosine similarity
        cache_folder =r"D:\AI\Embedding_models",
        show_progress=True

)
db = FAISS.from_documents(docs, embedding)

# Step 3: Create RAG Chain
# llm = OpenAI()
llm = ChatGroq(model='qwen/qwen3-32b')

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever())

def ask_knowledge_base(query):
    return qa_chain.invoke(query)

# Step 4: Collect complaint and interact with API
class ComplaintSession:
    def __init__(self):
        self.data = {
            "name": None,
            "phone_number": None,
            "email": None,
            "complaint_details": None
        }
        self.prompt_order = ["name", "phone_number", "email", "complaint_details"]

    def is_complete(self):
        return all(self.data.values())

    def next_prompt(self):
        for field in self.prompt_order:
            if not self.data[field]:
                return field
        return None

    def set_field(self, key, value):
        self.data[key] = value

    def submit_complaint(self):
        response = requests.post("http://localhost:8000/complaints", json=self.data)
        return response.json()

    def get_complaint_details(self, complaint_id):
        response = requests.get(f"http://localhost:8000/complaints/{complaint_id}")
        return response.json()



# class ComplaintSession:
#     def __init__(self):
#         self.data = {"name": None, "phone_number": None, "email": None, "complaint_details": None}
    
#     def is_complete(self):
#         return all(self.data.values())

#     def next_prompt(self):
#         for key, val in self.data.items():
#             if not val:
#                 return key
#         return None

#     def set_field(self, key, value):
#         self.data[key] = value

#     def submit_complaint(self):
#         response = requests.post("http://localhost:8000/complaints", json=self.data)
#         return response.json()
    
#     def get_complaint_details(self, complaint_id):
#         response = requests.get(f"http://localhost:8000/complaints/{complaint_id}")
#         return response.json()

import os
import shutil
import argparse
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")


# Constants
CHROMA_PATH = r"D:\AI\cursorAI\rag-app\chroma"
DATA_PATH = r"D:\AI\cursorAI\rag-app\data"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={"normalize_embeddings": True},  # Recommended for cosine similarity
        cache_folder =r"D:\AI\Embedding_models",
        show_progress=True
    )


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    pdf_folder = Path(DATA_PATH)
    documents = []

    for pdf_file in pdf_folder.glob("*.pdf"):
        print(f"Loading PDF: {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())

    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    if len(chunks) > 10:
        sample = chunks[10]
        print(sample.page_content)
        print(sample.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks, get_embeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


def query_knowledge_base(query_text: str):
    embedding_function = get_embeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print("\n🧠 Prompt sent to model:\n", prompt)

    # You can still use ChatOpenAI or replace this with a local model for full Hugging Face flow
    model = ChatGroq(model='qwen/qwen3-32b')
    response_text = model.predict(prompt)

    sources = [doc.metadata.get("source", None) for doc, _ in results]
    formatted_response = f"\n✅ Response:\n{response_text}\n\n📚 Sources: {sources}"
    print(formatted_response)


def main():
    parser = argparse.ArgumentParser(description="LangChain PDF QA with HuggingFace Embeddings")
    parser.add_argument("--build-db", action="store_true", help="Load PDF files and build vector DB")
    parser.add_argument("--query", type=str, help="Ask a question based on stored PDFs")
    args = parser.parse_args()

    if args.build_db:
        generate_data_store()
    elif args.query:
        query_knowledge_base(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

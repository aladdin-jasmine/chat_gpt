from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

async def build_knowledge_base(file_path: str):
    loader = TextLoader(file_path)
    docs = loader.load()

    split_docs = splitter.split_documents(docs)

    vector_db = FAISS.from_documents(
        split_docs,
        embedding
    )

    vector_db.save_local('faiss_index')

    return 'Knowledge base created'

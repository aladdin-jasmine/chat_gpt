from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceHub
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

memory = ConversationBufferMemory()

llm = HuggingFaceHub(
    repo_id='google/flan-t5-base',
    model_kwargs={'temperature': 0.5, 'max_length': 256}
)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

embedding = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)

vectorstore = Chroma(
    collection_name='chat_memory',
    embedding_function=embedding,
    persist_directory='./vector_db'
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

async def ask_ai(query: str):
    response = conversation.predict(input=query)

    docs = text_splitter.split_documents([
        Document(page_content=query),
        Document(page_content=response)
    ])

    vectorstore.add_documents(docs)

    return response

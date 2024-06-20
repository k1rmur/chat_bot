import os
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models.gigachat import GigaChat
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()
CREDENTIALS = os.getenv('CREDENTIALS', '0')

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db")

embeddings = GigaChatEmbeddings(
    credentials=CREDENTIALS, verify_ssl_certs=False
)

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)
db.get()

llm = GigaChat(credentials=CREDENTIALS, verify_ssl_certs=False)

qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

while True:
    question = input('Введите вопрос:\n')
    print(qa_chain({"query": question}))
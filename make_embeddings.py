import os
from langchain_community.document_loaders import PDFMinerLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from chromadb.config import Settings
from dotenv import load_dotenv

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db")

LOADER = PDFMinerLoader
print("Loading data...")
pdf_folder_path = "./data/"
files = [file for file in os.listdir(pdf_folder_path) if file.endswith(".pdf")]

loaders = [LOADER(os.path.join(pdf_folder_path, fn)) for fn in files]

print(loaders)

all_documents = []

for loader in loaders:
    print("Loading raw document..." + loader.file_path)
    raw_documents = loader.load()
    print(raw_documents[0])

    print("Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
    )
    documents = text_splitter.split_documents(raw_documents)
    all_documents.extend(documents)


load_dotenv()
CREDENTIALS = os.environ.get('CREDENTIALS', '0')

embeddings = GigaChatEmbeddings(
    credentials=CREDENTIALS, verify_ssl_certs=False
)

db = Chroma.from_documents(
    all_documents,
    embeddings,
    persist_directory=DB_DIR,
#    collection_name='documents_base'
)
db.persist()
print('БД сохранится в', DB_DIR)

db = None
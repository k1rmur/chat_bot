import os
from langchain_community.document_loaders import PDFMinerLoader, CSVLoader, Docx2txtLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from optparse import OptionParser
from langchain_community.vectorstores.chroma import Chroma
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

parser = OptionParser()
parser.add_option('--Mode', type=str, default="inner")
(Opts, args) = parser.parse_args()
mode = Opts.Mode


ABS_PATH = os.path.dirname(os.path.abspath(__file__))

PDF_LOADER = PDFMinerLoader
CSV_LOADER = CSVLoader
DOCX_LOADER = Docx2txtLoader
print("Loading data...")

if mode == "inner":
    folder_path = "./data/"
    DB_DIR = os.path.join(ABS_PATH, "db")
else:
    folder_path = "./data_citizens/"
    DB_DIR = os.path.join(ABS_PATH, "db_citizens")

pdf_files = [file for file in os.listdir(folder_path) if file.endswith(".pdf")]
csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]
docx_files = [file for file in os.listdir(folder_path) if file.endswith(".docx")]

pdf_loaders = [PDF_LOADER(os.path.join(folder_path, fn)) for fn in pdf_files]
csv_loaders = [CSV_LOADER(os.path.join(folder_path, fn), csv_args={"delimiter": ",", "quotechar": '"'}, encoding='utf-8-sig') for fn in csv_files]
docx_loaders = [DOCX_LOADER(os.path.join(folder_path, fn)) for fn in docx_files]
loaders = pdf_loaders + csv_loaders + docx_loaders

all_documents = []

for loader in loaders:
    print("Loading raw document..." + loader.file_path)
    raw_documents = loader.load()
    if loader.__class__ != CSVLoader:
        print("Splitting text...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=256,
            chunk_overlap=64,
        )
        documents = text_splitter.split_documents(raw_documents)
        all_documents.extend(documents)
    else:
        all_documents.extend(raw_documents)

print("Splitting is finished")

load_dotenv()
CREDENTIALS = os.environ.get('CREDENTIALS', '0')

embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

db = Chroma.from_documents(
    all_documents,
    embeddings,
    persist_directory=DB_DIR
)
db.persist()
print('БД сохранится в', DB_DIR)

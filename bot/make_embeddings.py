import os
from optparse import OptionParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader, Settings, StorageContext, VectorStoreIndex
from langchain_community.chat_models import ChatOllama
import torch
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore


parser = OptionParser()
parser.add_option('--Mode', type=str, default="inner")
(Opts, args) = parser.parse_args()
mode = Opts.Mode

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
#PDF_LOADER = PDFMinerLoader
#CSV_LOADER = CSVLoader
#DOCX_LOADER = Docx2txtLoader
#print("Loading data...")
if mode == "inner":
    folder_path = "/app/bot/data/"
    DB_DIR = os.path.join(ABS_PATH, "db")
else:
    folder_path = "/app/bot/data_citizens/"
    DB_DIR = os.path.join(ABS_PATH, "db_citizens")

reader = SimpleDirectoryReader(folder_path)

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print("DEVICE:", device)
embeddings = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-small", device=device)
Settings.embed_model = embeddings
Settings.chunk_size = 512
Settings.chunk_overlap = 128


if __name__ == '__main__':

    llm = ChatOllama(model='llama3.1', temperature=0.1, base_url="http://ollama-container-gpu:11434", keep_alive=-1, num_ctx=1024, num_gpu=33)
    Settings.llm = llm

    documents = reader.load_data()

    try:
        os.remove(f'{DB_DIR}/chroma.sqlite3')
    except:
        pass
    db = chromadb.PersistentClient(path=DB_DIR)
    chroma_collection = db.create_collection("embeddings")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

else:

    db = chromadb.PersistentClient(path=DB_DIR)

    chroma_collection = db.get_or_create_collection("embeddings")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )

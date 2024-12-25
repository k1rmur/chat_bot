import os
from optparse import OptionParser

import chromadb
import torch
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

parser = OptionParser()
parser.add_option("--Mode", type=str, default="inner")
(Opts, args) = parser.parse_args()
mode = Opts.Mode

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

if mode == "inner":
    folder_path = "/app/bot/data/"
    DB_DIR = os.path.join(ABS_PATH, "db")
else:
    folder_path = "/app/bot/data_citizens/"
    DB_DIR = os.path.join(ABS_PATH, "db_citizens")

reader = SimpleDirectoryReader(folder_path)

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print("DEVICE:", device)
embeddings = HuggingFaceEmbedding(
    model_name="intfloat/multilingual-e5-small", device=device
)
Settings.embed_model = embeddings


if __name__ == "__main__":
    try:
        os.remove(f"{DB_DIR}/chroma.sqlite3")
    except:
        pass

    documents = reader.load_data()
    parser = TokenTextSplitter(chunk_size=1024, chunk_overlap=256)
    nodes = parser.get_nodes_from_documents(documents)
    print(nodes)
    docstore = SimpleDocumentStore()
    docstore.add_documents(nodes)

    bm25_retriever = BM25Retriever.from_defaults(docstore=docstore, similarity_top_k=5)

    db = chromadb.PersistentClient(path=DB_DIR)
    chroma_collection = db.create_collection("embeddings")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

    docstore.persist(f"{DB_DIR}/docstore")

else:
    try:
        docstore = SimpleDocumentStore.from_persist_path(f"{DB_DIR}/docstore")
    except Exception:
        documents = reader.load_data()
        parser = TokenTextSplitter(chunk_size=1024, chunk_overlap=256)
        nodes = parser.get_nodes_from_documents(documents)
        docstore = SimpleDocumentStore()
        docstore.add_documents(nodes)
        docstore.persist(f"{DB_DIR}/docstore")

    db = chromadb.PersistentClient(path=DB_DIR)

    chroma_collection = db.get_or_create_collection("embeddings")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )

    bm25_retriever = BM25Retriever.from_defaults(docstore=docstore, similarity_top_k=5)

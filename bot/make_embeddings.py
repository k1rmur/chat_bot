import os

import chromadb
import torch
from llama_index.core import (Settings, SimpleDirectoryReader, StorageContext,
                              VectorStoreIndex)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

mode = "outer"

ABS_PATH = os.path.dirname(os.path.abspath(__file__))


folder_path = "/app/bot/data_citizens/"
DB_DIR = os.path.join(ABS_PATH, "db_citizens")

reader = SimpleDirectoryReader(folder_path)

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print("DEVICE:", device)
embeddings = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-small", device=device)
Settings.embed_model = embeddings
Settings.chunk_size = 256
Settings.chunk_overlap = 64


if __name__ == "__main__":

    documents = reader.load_data()
    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(documents)
    docstore = SimpleDocumentStore()
    docstore.add_documents(nodes)

    db = chromadb.PersistentClient(path=DB_DIR)
    chroma_collection = db.create_collection("embeddings")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    vector_index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)

    bm25_retriever = BM25Retriever.from_defaults(
        docstore=docstore, similarity_top_k=5
    )
    print("Vector index is created.")

    docstore.persist(f"{DB_DIR}/docstore")

else:
    docstore = SimpleDocumentStore.from_persist_path(f"{DB_DIR}/docstore")

    db = chromadb.PersistentClient(path=DB_DIR)

    chroma_collection = db.get_or_create_collection("embeddings")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )

    bm25_retriever = BM25Retriever.from_defaults(
        docstore=docstore, similarity_top_k=5
    )


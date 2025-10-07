import os

import chromadb
import Stemmer
import torch
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore


class CustomNodeParser(SentenceSplitter):
    def get_nodes_from_documents(self, documents):
        nodes = []
        for doc in documents:
            filename = os.path.splitext(
                os.path.basename(doc.metadata.get("file_path", ""))
            )[0]
            split_nodes = super().get_nodes_from_documents([doc])

            for node in split_nodes:
                node.text = f"Источник: {filename}\n\n{node.text}"
                node.metadata = {}  # Remove metadata
                nodes.append(node)

        return nodes


CHUNK_SIZE = 1024
CHUNK_OVERLAP = 256


ABS_PATH = os.path.dirname(os.path.abspath(__file__))

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
    except Exception:
        pass

    documents = reader.load_data()
    parser = CustomNodeParser(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    vector_parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents(documents)
    vector_nodes = vector_parser.get_nodes_from_documents(documents)
    print(nodes)
    docstore = SimpleDocumentStore()
    docstore.add_documents(nodes)

    bm25_retriever = BM25Retriever.from_defaults(
        docstore=docstore,
        similarity_top_k=20,
        stemmer=Stemmer.Stemmer("russian"),
        language="russian",
    )

    db = chromadb.PersistentClient(path=DB_DIR)
    chroma_collection = db.create_collection("embeddings")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex(vector_nodes, storage_context=storage_context)

    docstore.persist(f"{DB_DIR}/docstore")

else:
    try:
        docstore = SimpleDocumentStore.from_persist_path(f"{DB_DIR}/docstore")
    except Exception:
        documents = reader.load_data()
        parser = CustomNodeParser(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
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

    bm25_retriever = BM25Retriever.from_defaults(
        docstore=docstore,
        similarity_top_k=20,
        stemmer=Stemmer.Stemmer("russian"),
        language="russian",
    )

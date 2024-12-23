import os

from dotenv import find_dotenv, load_dotenv
from langchain_community.chat_models import GigaChat
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate
from llama_index.core.retrievers import QueryFusionRetriever
from make_embeddings import bm25_retriever, embeddings, vector_index

from .prompt_templates import (
    QA_PROMPT_STR,
    QA_SYSTEM_PROMPT,
    REFINE_PROMPT_STR,
)


async def get_context_str(text):
    documents = await retriever.aretrieve(text)
    doc_list = []
    current_string = ""
    for i, node in enumerate(documents):
        current_string += "---------\n"
        current_string += (
            f"Имя файла: {node.metadata.get('file_name', '')}\nСодержание:\n"
        )

        current_string += node.text

        doc_list.append(current_string)
        current_string = ""

    return "\n\n".join(doc_list)


load_dotenv(find_dotenv())

CREDENTIALS = os.getenv("CREDENTIALS")


chat_text_qa_msgs = [
    SystemMessagePromptTemplate.from_template(QA_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(QA_PROMPT_STR),
]
text_qa_template = ChatPromptTemplate.from_messages(chat_text_qa_msgs)


chat_refine_msgs = [
    (
        "system",
        QA_SYSTEM_PROMPT,
    ),
    ("user", REFINE_PROMPT_STR),
]
refine_template = ChatPromptTemplate.from_messages(chat_refine_msgs)


llm = GigaChat(
    verify_ssl_certs=False,
    credentials=CREDENTIALS,
    scope="GIGACHAT_API_CORP",
    model="GigaChat-Pro",
    verbose=True,
    profanity=False,
    temperature=0.1,
)
Settings.llm = llm
Settings.embed_model = embeddings
Settings.context_window = 32768


vector_retriever = vector_index.as_retriever(similarity_top_k=5)

retriever = QueryFusionRetriever(
    [bm25_retriever, vector_retriever],
    similarity_top_k=10,
    num_queries=1,
    mode="reciprocal_rerank",
    use_async=True,
    verbose=True,
)

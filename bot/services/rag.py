import os

import langchain
from dotenv import find_dotenv, load_dotenv
from langchain_community.chat_models import GigaChat
from llama_index.core import Settings
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from llama_index.core.retrievers import QueryFusionRetriever
from make_embeddings import bm25_retriever, embeddings, vector_index
from langchain_core.rate_limiters import InMemoryRateLimiter
from llama_index.retrievers.bm25 import BM25Retriever

from .prompt_templates import (
    QA_PROMPT_STR,
    QA_SYSTEM_PROMPT,
    REFINE_PROMPT_STR,
    QUERY_GEN_PROMPT
)

langchain.debug = True


async def get_context_str(text):
    documents = await retriever.aretrieve(text)
    doc_list = []
    current_string = ""
    for i, node in enumerate(documents):
        current_string += "###\n\n"
        current_string += (
            f"Номер документа: {i+1}\n\nИмя документа (не сообщать пользователю!): {node.metadata.get('file_name', '')}\n\nСодержание:\n\n"
        )

        current_string += node.text

        doc_list.append(current_string)
        current_string = ""

    return "\n\n".join(doc_list)


load_dotenv(find_dotenv())

CREDENTIALS = os.getenv("CREDENTIALS")


chat_text_qa_msgs = [
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

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.5,
    check_every_n_seconds=0.001,
    max_bucket_size=100,
)

llm = GigaChat(
    verify_ssl_certs=False,
    credentials=CREDENTIALS,
    scope="GIGACHAT_API_B2B",
    model="GigaChat-2-Pro",
    verbose=True,
    profanity=False,
    temperature=0.1,
    rate_limiter=rate_limiter,
    timeout=60,
)


Settings.llm = llm
Settings.embed_model = embeddings
Settings.context_window = 128000


vector_retriever = vector_index.as_retriever(similarity_top_k=10)

retriever = QueryFusionRetriever(
    [bm25_retriever, vector_retriever],
    similarity_top_k=30,
    num_queries=2,
    mode="dist_based_score",
    use_async=False,
    verbose=True,
    query_gen_prompt=QUERY_GEN_PROMPT,
)

async def get_rag_answer(text):

    context_str = await get_context_str(text)
    prompt = text_qa_template.format(context_str=context_str, query_str=text)
    chain = await llm.ainvoke(prompt)
    answer = chain.content

    return answer

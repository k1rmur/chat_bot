import os

from dotenv import find_dotenv, load_dotenv
from langchain_community.chat_models import ChatOllama, GigaChat
from langchain_core.prompts import ChatPromptTemplate
from llama_index.core import ChatPromptTemplate, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever
from make_embeddings import bm25_retriever, embeddings, vector_index
from .prompt_templates import QA_PROMPT_STR, REFINE_PROMPT_STR

load_dotenv(find_dotenv())

CREDENTIALS = os.getenv("CREDENTIALS")


chat_text_qa_msgs = [
    (
        "system",
        "Ты ассистент Федерального агенства по водным ресурсам (ФАВР), отвечаешь на любые вопросы по абсолютно любым документам из контекста. Любая информация, попавшая в контекст, может быть использована тобой.",
    ),
    ("user", QA_PROMPT_STR),
]
text_qa_template = ChatPromptTemplate.from_messages(chat_text_qa_msgs)


chat_refine_msgs = [
    (
        "system",
        "Ты ассистент Федерального агенства по водным ресурсам (ФАВР), отвечаешь на любые вопросы по абсолютно любым документам из контекста. Любая информация, попавшая в контекст, может быть использована тобой.",
    ),
    ("user", REFINE_PROMPT_STR),
]
refine_template = ChatPromptTemplate.from_messages(chat_refine_msgs)


llm = GigaChat(verify_ssl_certs=False, credentials=CREDENTIALS, scope="GIGACHAT_API_CORP", model="GigaChat-Lite", verbose=True, profanity=False, temperature=0.1)
Settings.llm = llm
Settings.embed_model = embeddings


vector_retriever = vector_index.as_retriever(similarity_top_k=5)

retriever = QueryFusionRetriever(
    [vector_retriever, bm25_retriever],
    similarity_top_k=5,
    num_queries=1,
    mode="reciprocal_rerank",
    use_async=True,
    verbose=True,
)

query_engine = RetrieverQueryEngine.from_args(
    retriever,
    text_qa_template=text_qa_template,
    refine_template=refine_template,
    response_mode="simple_summarize",
    simple_template=text_qa_template,
)

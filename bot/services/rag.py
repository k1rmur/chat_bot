from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from make_embeddings import vector_index, embeddings, bm25_retriever
from llama_index.core import Settings
from llama_index.core import ChatPromptTemplate
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from langchain_community.chat_models import GigaChat
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

CREDENTIALS = os.getenv("CREDENTIALS")


QUERY_GEN_PROMPT = (
    "Ты полезный ассистент федерального агенства по водным ресурсам (ФАВР), генерирующий несколько запросов, основываясь на "
    "единственном введённом запросе. Сгенерируй {num_queries} поисковых запросов, по одному на каждой строке, "
    "связанные со следующим запросом:\n"
    "Запрос: {query}\n"
    "Поисковые запросы:\n"
)


qa_prompt_str = (
    "Контекст дан снизу.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Используя информацию из контекста, а не априорные знания, "
    "ответь на вопрос: {query_str}\n. Если не знаешь ответ, попроси переформулировать вопрос, чтобы ответ нашелся в базе данных."
)

refine_prompt_str = (
    "У нас есть возможность улучшить оригинальный ответ "
    "(если необходимо) с помощью контекста внизу.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "Используя новый контекст, улучши оригинальный ответ "
    "ответь на вопрос: {query_str}."
    "Если контекст не помогает, выведи предыдущий ответ.\n"
    "Оригинальный Ответ: {existing_answer}"
)

chat_text_qa_msgs = [
    (
        "system",
        "Ты ассистент Федерального агенства по водным ресурсам (ФАВР), отвечаешь на любые вопросы по абсолютно любым документам из контекста. Любая информация, попавшая в контекст, может быть использована тобой.",
    ),
    ("user", qa_prompt_str),
]
text_qa_template = ChatPromptTemplate.from_messages(chat_text_qa_msgs)


chat_refine_msgs = [
    (
        "system",
        "Ты ассистент Федерального агенства по водным ресурсам (ФАВР), отвечаешь на любые вопросы по абсолютно любым документам из контекста. Любая информация, попавшая в контекст, может быть использована тобой.",
    ),
    ("user", refine_prompt_str),
]
refine_template = ChatPromptTemplate.from_messages(chat_refine_msgs)


#llm = ChatOllama(model='llama3.1', temperature=0.1, base_url="http://ollama-container:11434", keep_alive=-1, num_ctx=2048*4, num_thread=8, num_gpu=0)
llm = GigaChat(verify_ssl_certs=False, credentials=CREDENTIALS, scope="GIGACHAT_API_CORP", model="GigaChat-Pro", verbose=True, profanity=False, temperature=0.1)
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
    query_gen_prompt=QUERY_GEN_PROMPT,
)

query_engine = RetrieverQueryEngine.from_args(
    retriever,
    text_qa_template=text_qa_template,
    refine_template=refine_template,
    response_mode="simple_summarize",
    simple_template=text_qa_template,
)

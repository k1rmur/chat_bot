from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from make_embeddings import vector_index, embeddings
from llama_index.core import Settings
from llama_index.core import ChatPromptTemplate


qa_prompt_str = (
    "Контекст дан снизу.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Используя информацию из контекста, а не априорные знания, "
    "ответь на вопрос: {query_str}\n."
)

refine_prompt_str = (
    "У нас есть возможность улучшить оригинальный ответ "
    "(если необходимо) с помощью контекста внизу.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "Используя новый контекст, улучши оригинальный ответ "
    "ответь на вопрос: {query_str}."
    "Если контекст не помогает,выведи предыдущий ответ.\n"
    "Оригинальный Ответ: {existing_answer}"
)

chat_text_qa_msgs = [
    (
        "system",
        "Ты ассистент Федерального агенства по водным ресурсам (ФАВР), отвечаешь на вопросы по документам из базы данных (в том числе по запросу можешь отправлять контакты начальников ФАВР). Если контекст не помогает, не отвечай на вопрос. Не используй MarkDown",
    ),
    ("user", qa_prompt_str),
]
text_qa_template = ChatPromptTemplate.from_messages(chat_text_qa_msgs)


chat_refine_msgs = [
    (
        "system",
        "Ты ассистент Федерального агенства по водным ресурсам (ФАВР), отвечаешь на вопросы по документам из базы данных (в том числе по запросу можешь отправлять контакты начальников ФАВР). Если контекст не помогает, не отвечай на вопрос. Не используй MarkDown",
    ),
    ("user", refine_prompt_str),
]
refine_template = ChatPromptTemplate.from_messages(chat_refine_msgs)


llm = ChatOllama(model='llama3.1', temperature=0.1, base_url="http://ollama-container:11434", keep_alive=-1, num_ctx=2048*2, num_thread=8, num_gpu=0)
Settings.llm = llm
Settings.embed_model = embeddings


index = vector_index.as_query_engine(
    text_qa_template=text_qa_template,
    refine_template=refine_template,
    llm=llm,
)
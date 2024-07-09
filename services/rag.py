import os
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import services.initialize_db_name  as db_name
from dotenv import load_dotenv
from g4f import models, Provider
from langchain.llms.base import LLM

from langchain_g4f import G4FLLM


load_dotenv()
CREDENTIALS = os.getenv('CREDENTIALS', '0')

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
if db_name.db_name == 'inner':
    DB_DIR = os.path.join(ABS_PATH, "../db")
elif db_name.db_name == 'outer':
    DB_DIR = os.path.join(ABS_PATH, "../db_citizens")
else:
    raise Exception("Ошибка с инициализацией имени базы данных")

print(DB_DIR)

MESSAGE_THRESHOLD = 5

embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-m3")

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)
db.get()

llm: LLM = G4FLLM(
    model=models.gpt_35_turbo,
    provider=Provider.You
)

retriever = db.as_retriever()


### Переформулирование вопроса ###
contextualize_q_system_prompt = """Имея историю чата и последний вопрос пользователя, \
который может ссылаться на контекст в истории чата, сформулируй самостоятельный вопрос, \
который можно понять без истории чата. НЕ ОТВЕЧАЙ на вопрос, \
просто переформулируй его при необходимости, иначе верни его как есть."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)


if db_name.db_name == 'inner':
    qa_system_prompt = """Ты ассистент для сотрудников Федерального Агенства Водных Ресурсов \
    (ФАВР), твоя единственная функция - отвечать на вопросы по документам из базы данных. \
    Используй ТОЛЬКО следующий контекст для ответа на вопрос, не пользуясь своими начальными знаниями. \
    Если ответа нет в базе данных, не пиши ответ на него. \
    Отвечай кратко и ёмко, пиши только на русском языке.\
    Контекст:\
    {context}\
    Конец контекста."""
else:
    qa_system_prompt = """Ты ассистент Федерального Агенства Водных Ресурсов для граждан, \
    твоя единственная функция - отвечать на вопросы граждан по документам из базы данных. \
    Используй ТОЛЬКО следующий контекст для ответа на вопрос, не пользуясь своими начальными знаниями. \
    Если ответа нет в базе данных, не пиши ответ на него. \
    Отвечай кратко и ёмко, пиши только на русском языке.\
    Контекст:\
    {context}\
    Конец контекста."""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


### Состояние для работы с историей чата ###
conversation_history = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in conversation_history:
        conversation_history[session_id] = ChatMessageHistory()
    return conversation_history[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

import os
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models.gigachat import GigaChat
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


load_dotenv()
CREDENTIALS = os.getenv('CREDENTIALS', '0')
BOT_TOKEN = os.getenv('BOT_TOKEN', '0')


ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db")

embeddings = GigaChatEmbeddings(
    credentials=CREDENTIALS, verify_ssl_certs=False
)

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)
db.get()

llm = GigaChat(credentials=CREDENTIALS, verify_ssl_certs=False)


retriever = db.as_retriever()


### Переформулирование вопроса ###
contextualize_q_system_prompt = """Имея историю чата и последний вопрос пользователя, \
который может ссылаться на контекст в истории чата, сформулируй самостоятельный вопрос, \
который можно понять без истории чата. Не ОТВЕЧАЙ на вопрос, \
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


### Ответ на вопрос ###
qa_system_prompt = """Ты ассисент для ответов на вопросы по документам, которые касаются Федерального Агенства Водных Ресурсов. \
Используй следующий контекст для ответа на вопрос. \
Если ответа нет в базе данных, напиши об этом. \
Отвечай кратко и ёмко.\

{context}"""
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
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!')

@dp.message()
async def send_echo(message: Message):
    answer = conversational_rag_chain.invoke(
        {"input": message.text},
        config={
            "configurable": {"session_id": "abc123"}
        }
    )["answer"]
    print(message.text)
    print(answer)
    await message.reply(text=answer)


if __name__ == '__main__':
    dp.run_polling(bot)
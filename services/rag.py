import os
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import services.initialize_db_name  as db_name
from dotenv import load_dotenv
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate


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

MESSAGE_THRESHOLD = 3


embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)
db.get()

model_path = os.path.join(ABS_PATH, "models/model-q4_K.gguf")

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
  model_path=model_path,
  temperature=0.1,
  top_p=0.9,
  top_k=30,
  n_ctx=8192,
  n_threads=8,
  f16_kv=True,
  verbose=True,
  callback_manager=callback_manager
)

retriever = db.as_retriever()

rephrase_template = '''<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Ты ассистент Федерального агенства водных ресурсов (ФАВР). Учитывая историю чата и последний вопрос пользователя, который может ссылаться на историю чата, перефразируй этот вопрос в самостоятельный вопрос, который можно понять без истории чата. История чата: {chat_history} Если последний вопрос не связан с историей чата, просто перефразируй этот вопрос или оставь как есть.<|eot_id|><|start_header_id|>user<|end_header_id|>

{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Перефразированный вопрос в одно предложение:'''

qa_template = '''<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Ты - полезный, уважительный и честный ассистент Федерального агенства водных ресурсов (ФАВР). Всегда отвечай как можно более надежно. В ответах не должно быть информации из твоей базы знаний, а только лишь информация из контекста и ее перефразирование. Если вопрос не имеет смысла или не является фактологически последовательным, объясни почему, а не отвечай на вопрос некорректно. Если ты не знаешь ответа на вопрос, пожалуйста, не сообщай ложную информацию. Твоя цель - дать ответы, связанные с базой знаний ФАВР. База знаний: {context} История чата: {chat_history}<|eot_id|><|start_header_id|>user<|end_header_id|>

{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Вот краткий ответ на Ваш вопрос:'''


contextualize_q_prompt = PromptTemplate.from_template(rephrase_template)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_prompt = PromptTemplate.from_template(qa_template)
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

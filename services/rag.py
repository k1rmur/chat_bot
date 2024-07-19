import os
import torch
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
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline
import transformers
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler


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


embeddings = HuggingFaceBgeEmbeddings(model_name="deepvk/USER-bge-m3")

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)
db.get()

#quantization_config = BitsAndBytesConfig(
#    llm_int8_enable_fp32_cpu_offload=True,
#    load_in_8bit=True,
#)
#
#model = AutoModelForCausalLM.from_pretrained(
#    MODEL_NAME,
#    quantization_config=quantization_config,
#    torch_dtype=torch.bfloat16,
#    device_map="auto"
#)
#model.eval()
#
#tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#
#query_pipeline = transformers.pipeline(
#    "text-generation",
#    model=model,
#    tokenizer=tokenizer,
#    torch_dtype=torch.bfloat16,
#    device_map="auto",
#)
#
#llm = HuggingFacePipeline(pipeline=query_pipeline)

model_path = os.path.join(ABS_PATH, "models/saiga_llama3_8b.Q5_0.gguf")

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
  model_path=model_path,
  n_ctx=2048,
  n_threads=8,
  f16_kv=True,
  verbose=True,
  callback_manager=callback_manager
)

retriever = db.as_retriever()


### Переформулирование вопроса ###
contextualize_q_system_prompt = """Имея историю чата и последний вопрос пользователя, \
который может ссылаться на контекст в истории чата, сформулируй самостоятельный вопрос, \
который можно понять без истории чата. НЕ ОТВЕЧАЙ на вопрос, \
просто переформулируй его при необходимости, иначе верни его как есть."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", f'<|im_start|>\n{contextualize_q_system_prompt}<|im_end|>'),
#        MessagesPlaceholder("chat_history", n_messages=1),
        ("user", "<|im_start|>\n{input}<|im_end|><|im_start|>assistant"),
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
    Отвечай кратко и ёмко.\
    Контекст:\
    {context}\
    Конец контекста."""
else:
    qa_system_prompt = """Ты ассистент Федерального Агенства Водных Ресурсов для граждан, \
    твоя единственная функция - отвечать на вопросы граждан по документам из базы данных. \
    Используй ТОЛЬКО следующий контекст для ответа на вопрос, не пользуясь своими начальными знаниями. \
    Если ответа нет в базе данных, не пиши ответ на него. \
    Отвечай кратко и ёмко.\
    Контекст:\
    {context}\
    Конец контекста."""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", f'<|im_start|>\n{qa_system_prompt}<|im_end|>'),
#        MessagesPlaceholder("chat_history", n_messages=1),
        ("user", "<|im_start|>\n{input}<|im_end|><|im_start|>assistant"),
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

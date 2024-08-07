import os

from langchain.chains.llm import LLMChain
from docx import Document
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


load_dotenv(find_dotenv())

sys_prompt = """Перед тобой стенограмма совещания сотрудников Федерального агенства по водным ресурсам, напиши по ним следующие разделы, каждый раздел протокола должен иметь название и должен быть разделен отступом:
1) Вопрос совещания: основной вопрос, который обсуждался на совещании. Формулировка вопроса должна содержать не более 10 слов. 
2) Краткое резюме совещания: должен содержать краткий пересказ ключевых тем, поручений и решений совещания. Раздел должен состоять как минимум из трёх предложений.
3) Поручения: список поручений, которые были даны сотрудникам в ходе совещания. При формулировке каждого поручения необходимо указать сотрудника, кому было дано поручение, а также дату, к которой поручение необходимо исполнить. Формулировка каждого поручения должна содержать не менее 10 слов.
4) Содержание встречи:  не менее 3 основных тем, которые обсуждались на встрече. По каждой теме необходимо сформировать абзац, который будет иметь следующую структуру: первое предложение – тема, которая обсуждалась на встрече. Последующие предложения – информация по теме, которая содержится в стенограмме. Абзац в совокупности должен содержать не менее 4 предложений.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            sys_prompt,
        ),
        ("human", "Начало стенограммы:\n {input}\nКонец стенограммы."),
    ]
)


ABS_PATH = os.path.dirname(os.path.abspath(__file__))

llm = ChatOllama(model='llama3.1', temperature=0.2, base_url="http://ollama-container:11434", keep_alive=-1, num_ctx=2048, num_thread=8, num_gpu=0)

llm_chain = LLMChain(llm=llm, prompt=prompt)


async def get_summary(file_id, text):
    doc = Document()
    protocol = await llm_chain.arun(text)
    doc.add_paragraph(protocol)
    doc.save(f"./tmp/{file_id}.docx")  
    return f"./tmp/{file_id}.docx", "Протокол.docx"
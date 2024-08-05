import os

from langchain.chains.llm import LLMChain
from docx import Document
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


load_dotenv(find_dotenv())

sys_prompt = """Перед тобой стенограмма совещания, напиши два абзаца. Первый абзац - резюме совещания, второй - поручения для сотрудников, обсужденные на совещании. Если не было поручений - так и напиши. Если стенограмма пустая, не пиши ничего. Поручения и резюме бери только из стенограммы."""

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
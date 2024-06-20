import os
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models.gigachat import GigaChat

db = Chroma(persist_directory="./chroma_db")

CREDENTIALS = os.getenv('CREDENTIALS', '0')

llm = GigaChat(credentials=CREDENTIALS, verify_ssl_certs=False)

qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

while True:
    question = input('Введите вопрос:\n')
    print(qa_chain({"query": question}))
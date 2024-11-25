import glob
import logging
import operator
import os
from typing import Annotated, List, Literal, TypedDict

from docx import Document
from langchain.chains.combine_documents.reduce import (acollapse_docs,
                                                       split_list_of_docs)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langchain_community.chat_models import ChatOllama, GigaChat


def clear_temp(file_id):
    files = glob.glob('./tmp/*')
    for f in files:
        if file_id in f:
            print(f'Deleting {f}...')
            os.remove(f)
    files = glob.glob('app/bot/tmp/*')
    for f in files:
        if file_id in f:
            print(f'Deleting {f}...')
            os.remove(f)


llm = GigaChat(verify_ssl_certs=False, credentials=os.getenv("CREDENTIALS"), scope="GIGACHAT_API_CORP", model="GigaChat")

map_template = "Напиши краткое, но с сохранением главной информации обобщение следующего текста:\n{context}\n\nОбобщение:\n\n"

reduce_template = """
Ниже дан список обобщенных документов:
{docs}
Используя его, напиши финальное обобщение
главных тем.

Обобщение:

"""

map_prompt = ChatPromptTemplate([("human", map_template)])
reduce_prompt = ChatPromptTemplate([("human", reduce_template)])

map_chain = map_prompt | llm | StrOutputParser()
reduce_chain = reduce_prompt | llm | StrOutputParser()


logger = logging.getLogger(__name__)


def length_function(documents: List[Document]) -> int:
    """Get number of tokens for input contents."""
    return sum(llm.get_num_tokens(doc) for doc in documents)


token_max = 7000*5


class OverallState(TypedDict):
    contents: List[str]
    summaries: Annotated[list, operator.add]
    collapsed_summaries: List[Document]  # add key for collapsed summaries
    final_summary: str


class SummaryState(TypedDict):
    content: str


# Add node to store summaries for collapsing
def collect_summaries(state: OverallState):
    return {
        "collapsed_summaries": [summary for summary in state["summaries"]]
    }


def map_summaries(state: OverallState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    return [
        Send("generate_summary", {"content": content}) for content in state["contents"]
    ]


# Modify final summary to read off collapsed summaries
async def generate_final_summary(state: OverallState):
    response = await reduce_chain.ainvoke(state["collapsed_summaries"])
    return {"final_summary": response}


async def generate_summary(state: SummaryState):
    response = await map_chain.ainvoke(state["content"])
    return {"summaries": [response]}


graph = StateGraph(OverallState)
graph.add_node("generate_summary", generate_summary)  # same as before
graph.add_node("collect_summaries", collect_summaries)
graph.add_node("generate_final_summary", generate_final_summary)


# Add node to collapse summaries
async def collapse_summaries(state: OverallState):
    doc_lists = split_list_of_docs(
        state["collapsed_summaries"], length_function, token_max
    )
    results = []
    for doc_list in doc_lists:
        results.append(await acollapse_docs(doc_list, reduce_chain.ainvoke))

    return {"collapsed_summaries": results}


graph.add_node("collapse_summaries", collapse_summaries)


def should_collapse(
    state: OverallState,
) -> Literal["collapse_summaries", "generate_final_summary"]:
    num_tokens = length_function(state["collapsed_summaries"])
    if num_tokens > token_max:
        return "collapse_summaries"
    else:
        return "generate_final_summary"


graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
graph.add_edge("generate_summary", "collect_summaries")
graph.add_conditional_edges("collect_summaries", should_collapse)
graph.add_conditional_edges("collapse_summaries", should_collapse)
graph.add_edge("generate_final_summary", END)
app = graph.compile()


async def return_summary(documents):
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=40000, chunk_overlap=200
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Generated {len(split_docs)} documents.")
    step = None
    for step in app.stream(
        {"contents": [doc.page_content for doc in split_docs]},
        {"recursion_limit": 50},
    ):
        _ = step
    if step:
        return step["generate_final_summary"]["final_summary"]
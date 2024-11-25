import glob
import logging
import operator
import os
from typing import Annotated, List, Literal, TypedDict

from docx import Document
from langchain.chains.combine_documents.reduce import (acollapse_docs,
                                                       split_list_of_docs)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
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


CONTEXT_LENGTH = 8192*4

llm = GigaChat(verify_ssl_certs=False, credentials=os.getenv("CREDENTIALS"), scope="GIGACHAT_API_CORP", model="GigaChat")

map_template = "Напиши краткое, но с сохранением главной информации обобщение следующего текста:\n{context}\n\nОбобщение:\n\n"

map_facts_template = "Перед тобой новости водохозяйственной области. Выпиши факты и события из этого открывка:\n{context}\n\Факты и события:\n\n"
map_world_template = "Перед тобой новости о водохозяйственной области. Выпиши происходящее в мире из этого открывка:\n{context}\n\Происходящее в мире:\n\n"
map_conferences_template = "Перед тобой новости о водохозяйственной области. Выпиши конференции и выставки из этого открывка:\n{context}\n\Конференции и выставки:\n\n"

reduce_facts_template = """Ниже дан список фактов и событий водохозяйственной сферы:
{docs}
Используя его, напиши их обобщение

Обобщение:

"""
reduce_world_template = """Ниже дан список происходящего в мире в водохозяйственной сфере:
{docs}
Используя его, напиши их обобщение

Обобщение:

"""
reduce_conferences_template = """Ниже дан список конференций и выставок водохозяйственной сферы:
{docs}
Используя его, напиши их обобщение

Обобщение:

"""

reduce_template = """
Ниже дан список обобщенных документов:
{docs}
Используя его, напиши финальное обобщение
главных тем.

Обобщение:

"""

map_prompt = ChatPromptTemplate([("human", map_template)])
map_facts_prompt = ChatPromptTemplate(["human", map_facts_template])
map_world_prompt = ChatPromptTemplate(["human", map_world_template])
map_conferences_prompt = ChatPromptTemplate(["human",map_conferences_template])

reduce_prompt = ChatPromptTemplate([("human", reduce_template)])
reduce_facts_prompt = ChatPromptTemplate(["human", reduce_facts_template])
reduce_world_prompt = ChatPromptTemplate(["human", reduce_world_template])
reduce_conferences_prompt = ChatPromptTemplate(["human", reduce_conferences_template])

map_chain = map_prompt | llm | StrOutputParser()
map_facts_chain = map_facts_prompt | llm | StrOutputParser()
map_world_chain = map_world_prompt | llm | StrOutputParser()
map_conferences_chain = map_conferences_prompt | llm | StrOutputParser()

reduce_chain = reduce_prompt | llm | StrOutputParser()
reduce_facts_chain = reduce_facts_prompt | llm | StrOutputParser
reduce_world_chain = reduce_world_prompt | llm | StrOutputParser
reduce_conferences_chain = reduce_conferences_prompt | llm | StrOutputParser

logger = logging.getLogger(__name__)


def length_function(documents: List[Document]) -> int:
    """Get number of tokens for input contents."""
    return sum(llm.get_num_tokens(doc) for doc in documents)


token_max = 7000*4


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
async def generate_final_summary(state: OverallState, config):

    if config["configurable"].get("reduce_chain") is not None:
        reduce_chain = config["configurable"].get("reduce_chain")

    response = await reduce_chain.ainvoke(state["collapsed_summaries"])
    return {"final_summary": response}


async def generate_summary(state: SummaryState, config):

    if config["configurable"].get("map_chain") is not None:
        map_chain = config["configurable"].get("map_chain")

    response = await map_chain.ainvoke(state["content"])
    return {"summaries": [response]}


# Add node to collapse summaries
async def collapse_summaries(state: OverallState):
    doc_lists = split_list_of_docs(
        state["collapsed_summaries"], length_function, token_max
    )
    results = []
    for doc_list in doc_lists:
        results.append(await acollapse_docs(doc_list, reduce_chain.ainvoke))

    return {"collapsed_summaries": results}


def should_collapse(
    state: OverallState,
) -> Literal["collapse_summaries", "generate_final_summary"]:
    num_tokens = length_function(state["collapsed_summaries"])
    if num_tokens > token_max:
        return "collapse_summaries"
    else:
        return "generate_final_summary"


graph = StateGraph(OverallState)
graph.add_node("generate_summary", generate_summary)  # same as before
graph.add_node("collect_summaries", collect_summaries)
graph.add_node("generate_final_summary", generate_final_summary)
graph.add_node("collapse_summaries", collapse_summaries)
graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
graph.add_edge("generate_summary", "collect_summaries")
graph.add_conditional_edges("collect_summaries", should_collapse)
graph.add_conditional_edges("collapse_summaries", should_collapse)
graph.add_edge("generate_final_summary", END)
app = graph.compile()


async def return_summary(documents, mode=None):

    MODES = {
        "world": [map_world_chain, reduce_world_chain],
        "conferences": [map_conferences_chain, reduce_conferences_chain],
        "facts": [map_facts_chain, reduce_facts_chain]
    }

    if mode in MODES:
        map_chain, reduce_chain = MODES[mode]
        configurable = {
            "map_chain": map_chain,
            "reduce_chain": reduce_chain,     
        }
    else:
        configurable = dict()

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=20000, chunk_overlap=200
    )

    split_docs = text_splitter.split_documents(documents)
    print(f"Generated {len(split_docs)} documents.")
    step = None
    async for step in app.astream(
        {"contents": [doc.page_content for doc in split_docs]},
        {
            "recursion_limit": 50,
            "configurable": configurable
        },
    ):
        _ = step
    if step:
        return step["generate_final_summary"]["final_summary"]

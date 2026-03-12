from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI  # Or Anthropic/Grok
from langchain_community.tools import TavilySearchResults
from googleapiclient.discovery import build
import operator
import bs4  # For parsing if needed

llm = ChatOpenAI(model="gpt-4o")  # Swap as needed
search_tool = TavilySearchResults(max_results=5)
youtube = build('youtube', 'v3', developerKey='your_key')

class State(TypedDict):
    messages: Annotated[list, operator.add]
    research_data: str
    insights: str
    content_ideas: str

def researcher(state):
    query = state['messages'][-1].content
    web_results = search_tool.run(f"{query} youtube trends 2026")
    yt_results = youtube.search().list(q=query, part='snippet', maxResults=5, type='video').execute()
    data = f"Web: {web_results}\nYouTube: {yt_results}"
    return {"research_data": data, "messages": [HumanMessage(content=f"Researched: {data[:500]}...")]}

def analyzer(state):
    prompt = f"Analyze this data for YouTube content potential: {state['research_data']}. Extract trends, gaps, viral hooks."
    insights = llm.invoke(prompt).content
    return {"insights": insights}

def generator(state):
    prompt = f"From insights: {state['insights']}, generate 5 video ideas with titles, 1-min outlines, keywords, thumbnail ideas."
    ideas = llm.invoke(prompt).content
    return {"content_ideas": ideas, "messages": [HumanMessage(content=ideas)]}

workflow = StateGraph(State)
workflow.add_node("researcher", researcher)
workflow.add_node("analyzer", analyzer)
workflow.add_node("generator", generator)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "analyzer")
workflow.add_edge("analyzer", "generator")
workflow.add_edge("generator", END)
graph = workflow.compile()

# Run
inputs = {"messages": [HumanMessage(content="AI agent building for beginners")]}
result = graph.invoke(inputs)
print(result['content_ideas'])
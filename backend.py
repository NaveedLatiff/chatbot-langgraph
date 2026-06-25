from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model= "gemini-2.5-flash",
    google_api_key=api_key,
)

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    

def chat_node(state:ChatState):
    messages=state['messages']

    response=llm.invoke(messages)

    return {'messages':[response]}

checkpointer=MemorySaver()
graph=StateGraph(ChatState)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

workflow=graph.compile(checkpointer=checkpointer)


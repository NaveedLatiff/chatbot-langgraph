from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import  SqliteSaver
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import os
import sqlite3
import requests

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model= "gemini-3.5-flash",
    google_api_key=api_key,
)

# Tools

search_tool=DuckDuckGoSearchRun(region='us-en')

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a simple mathematical expression.
    Example: "3 + 4"
    """

    try:
        parts = expression.split()

        if len(parts) != 3:
            return "Use format: number operator number (e.g. '3 + 4')"

        num1 = float(parts[0])
        operator = parts[1]
        num2 = float(parts[2])

        if operator == "+":
            result = num1 + num2
        elif operator == "-":
            result = num1 - num2
        elif operator == "*":
            result = num1 * num2
        elif operator == "/":
            if num2 == 0:
                return "Error: Division by zero."
            result = num1 / num2
        else:
            return "Unsupported operator. Use +, -, *, /"

        if result.is_integer():
            return str(int(result))

        return str(result)

    except Exception as e:
        return f"Error: {e}"

@tool
def get_stock_price(symbol: str) -> str:
    """
    Get the latest stock price for a given stock symbol.
    Example symbols: AAPL, MSFT, TSLA, GOOGL.
    """

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol.upper(),
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "Global Quote" not in data or not data["Global Quote"]:
            return f"Could not find stock '{symbol}'."

        quote = data["Global Quote"]

        return (
            f"Stock: {quote['01. symbol']}\n"
            f"Price: ${quote['05. price']}\n"
            f"Change: {quote['09. change']}\n"
            f"Change Percent: {quote['10. change percent']}"
        )

    except Exception as e:
        return f"Error fetching stock price: {e}"


tools=[search_tool,calculator,get_stock_price]
llm_with_tools=llm.bind_tools(tools)


class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    

def chat_node(state:ChatState):
    """"LLM node that may answer or request a tool call."""
    messages=state['messages']

    response=llm_with_tools.invoke(messages)

    return {'messages':[response]}

tool_node = ToolNode(tools)

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)

checkpointer= SqliteSaver(conn=conn)

graph=StateGraph(ChatState)

graph.add_node('chat_node',chat_node)
graph.add_node('tools',tool_node)

graph.add_edge(START,'chat_node')
graph.add_conditional_edges(
    "chat_node",
    tools_condition
)
graph.add_edge("tools", "chat_node")

workflow=graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        
    return list(all_threads)   

res = workflow.invoke(
    {
        "messages": [
            HumanMessage(content="did u answer the stock price uestion from yourself or from th get_stock_price tool")
        ]
    },
    config={
        "configurable": {
            "thread_id": "1"
        }
    }
)

print(res["messages"][-1].content[0]['text'])

print(workflow.get_state(config={'configurable':{'thread_id':'1'}}))
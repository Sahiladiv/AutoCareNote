from langgraph.graph import StateGraph, END
from langchain.schema import BaseOutputParser
from prompts import SOAP_PROMPT, SUMMARY_PROMPT
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize Groq client

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL=os.getenv("GROQ_MODEL")
groq_client = Groq(api_key=GROQ_API_KEY)

# State
class State(dict):
    transcript: str
    soap: str
    summary: str

# SOAP Node
def soap_node(state: State):
    prompt = SOAP_PROMPT.format(transcript=state["transcript"])
    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,  # fast + high quality
        messages=[{"role": "user", "content": prompt}]
    )
    state["soap"] = resp.choices[0].message.content
    return state

# Summary Node
def summary_node(state: State):
    prompt = SUMMARY_PROMPT.format(transcript=state["transcript"])
    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    state["summary"] = resp.choices[0].message.content
    return state

# Build Graph
workflow = StateGraph(State)
workflow.add_node("soap", soap_node)
workflow.add_node("summary", summary_node)

workflow.set_entry_point("soap")
workflow.add_edge("soap", "summary")
workflow.add_edge("summary", END)

graph = workflow.compile()

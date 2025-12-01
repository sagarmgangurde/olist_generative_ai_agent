from fastapi import FastAPI
from agent.agent import ask_agent

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/ask")
def ask(q: str):
    answer = ask_agent(q)
    if not answer:
        answer = "Agent Error: No answer returned."
    return {"answer": answer}

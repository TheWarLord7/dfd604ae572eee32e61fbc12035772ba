import os
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OLLAMA_MODEL, DEFAULT_LLM_ENGINE
from vector import retreiver

# ---------------------------------------------------------------------------
# Model setup
# ---------------------------------------------------------------------------
if DEFAULT_LLM_ENGINE == "openrouter":
    model = ChatOpenAI(
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        model_name=OPENROUTER_MODEL,
        model_kwargs={
            "extra_headers": {
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Temple Preservation System"
            }
        }
    )
else:
    model = OllamaLLM(model=OLLAMA_MODEL)

chat_history = []


def optimize_search_query(q: str) -> str:
    prompt_str = f'''Analyze the user's research question about dilapidated temples.
Extract or rephrase it into key search terms containing: Location, Deities, or Architectural elements.

User Question: "{q}"

Output ONLY the finalized search keywords. Do not include introductory notes, conversational filler, or quotes.'''

    try:
        response = model.invoke(prompt_str)
        extracted = response.content.strip() if hasattr(response, 'content') else str(response).strip()
        if not extracted or len(extracted) < 2:
            return q
        return extracted
    except Exception:
        return q


system_template = '''You are a highly detailed historical preservation expert and archaeologist specialized in ancient Indian heritage.

Your mission is to answer user inquiries using ONLY the provided temple documentation chunks.

CRITICAL RULES FOR ACCURACY:
1. Grounding: Answer strictly from the provided text. If the text does not contain specific metrics, condition statuses, or historical records to satisfy the question, explicitly state: "Information not available in current documentation."
2. Individual Analysis: If multiple temples are retrieved, address each temple individually by name. Do not group them into an abstract, vague summary.
3. Transparency: Do not mention phrases like "According to the provided text blocks" or "Based on the data chunks." Present the data natively as your verified knowledge base.

Retrieved Temple Context Chunks:
{temples}

Recent Conversation Summary:
{context_summary}

Current Question: {question}
Answer:'''

prompt_processor = ChatPromptTemplate.from_template(system_template)
generation_chain = prompt_processor | model


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Temple Research API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    context_summary: Optional[str] = ""


@app.get("/health")
def health():
    return {"status": "ok", "model": DEFAULT_LLM_ENGINE}


@app.get("/search")
def search(q: str):
    q = (q or "").strip()
    if not q:
        return {"query": q, "results": []}

    search_term = optimize_search_query(q)
    docs = retreiver.invoke(search_term)
    results = []
    for doc in docs:
        results.append({
            "content": doc.page_content,
            "metadata": getattr(doc, "metadata", {})
        })
    return {"query": search_term, "results": results}


@app.post("/ask")
def ask(payload: AskRequest):
    question = (payload.question or "").strip()
    if not question:
        return {"answer": "Please provide a valid question.", "search_term": "", "sources": []}

    context_summary = payload.context_summary or ""
    for msg in chat_history[-6:]:
        prefix = "User: " if isinstance(msg, HumanMessage) else "AI: "
        context_summary += f"{prefix}{msg.content}\n"

    search_term = optimize_search_query(question)
    docs = retreiver.invoke(search_term)

    result = generation_chain.invoke({
        "temples": docs,
        "question": question,
        "context_summary": context_summary,
    })

    answer = result.content if hasattr(result, "content") else str(result)
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))

    sources = []
    for doc in docs:
        sources.append({
            "content": doc.page_content,
            "metadata": getattr(doc, "metadata", {})
        })

    return {
        "answer": answer,
        "search_term": search_term,
        "sources": sources,
    }


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)

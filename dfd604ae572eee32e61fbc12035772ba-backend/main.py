import os
from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OLLAMA_MODEL, DEFAULT_LLM_ENGINE
from vector import retreiver

# =====================================================================
# ENGINE CONFIGURATION
# =====================================================================

print("Select the LLM Execution Engine:")
print(f"1. Local Ollama ({OLLAMA_MODEL})")
print(f"2. OpenRouter Cloud API ({OPENROUTER_MODEL})")
choice = input("Enter choice (1 or 2) [default: {0}]: ".format(DEFAULT_LLM_ENGINE == "openrouter" and "2" or "1")).strip() or ("2" if DEFAULT_LLM_ENGINE == "openrouter" else "1")

if choice == "2":
    print("\n--> Configured via OpenRouter Cloud API...")
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
    print("\n--> Configured via Local Ollama...")
    model = OllamaLLM(model=OLLAMA_MODEL)

# Track conversational history using structured blocks rather than a runaway text string
chat_history = []

# =====================================================================
# SYSTEM PROMPTS & PIPELINES
# =====================================================================

def optimize_search_query(q):
    """
    Prevents empty search parameters. If specific metadata (location/deity) 
    can't be extracted cleanly, it falls back to a descriptive keyword phrase.
    """
    prompt_str = f'''Analyze the user's research question about dilapidated temples.
Extract or rephrase it into key search terms containing: Location, Deities, or Architectural elements.

User Question: "{q}"

Output ONLY the finalized search keywords. Do not include introductory notes, conversational filler, or quotes.'''
    
    try:
        response = model.invoke(prompt_str)
        extracted = response.content.strip() if hasattr(response, 'content') else str(response).strip()
        # Fallback if the model returns filler or blank data
        if not extracted or len(extracted) < 2:
            return q
        return extracted
    except Exception:
        return q  # Fail-safe: use raw query if API flaked

# Strict, grounded system prompt to eliminate hallucinations
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

# =====================================================================
# RUNTIME LOOP
# =====================================================================
while True:
    sep = '\n' + ('=' * 40)
    print(sep)
    question = input('Ask (q to exit): ').strip()
    print(sep)
    if question.lower() == 'q': 
        break
    if not question:
        continue

    # 1. Build a sliding-window history block (Last 3 interactions max) to protect the context window
    context_summary = ""
    for msg in chat_history[-6:]:
        prefix = "User: " if isinstance(msg, HumanMessage) else "AI: "
        context_summary += f"{prefix}{msg.content}\n"

    # 2. Optimize the search query dynamically
    search_term = optimize_search_query(question)
    print(f"[System Debug] Target Vector Search Query: '{search_term}'")
    
    # 3. Retrieve relevant artifacts from Chroma DB
    try:
        temples_docs = retreiver.invoke(search_term)
    except Exception as e:
        print(f"[Database Error] Retrieval failed: {e}")
        continue

    # 4. Generate the final authoritative response
    try:
        result = generation_chain.invoke({
            'temples': temples_docs, 
            'question': question, 
            'context_summary': context_summary
        })
        
        answer_text = result.content if hasattr(result, 'content') else str(result)
        print(answer_text)
        
        # Append to historical list
        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(content=answer_text))
        
    except Exception as e:
        print(f"[Generation Error] LLM engine failed to process: {e}")
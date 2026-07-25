from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver

model = OllamaLLM(model='gemma4:e4b')
# model = OllamaLLM(model='nemotron-3-nano:4b')

context = ''

def standardize_query(q):
    return model.invoke(f'''This is the query: "{q}"
                 you have to standardize the query into this format: location, [deities]
                 where [deities] are the deities user has mentioned in the query and in formating are supposed to be separated by comma''')


template = '''
You are an expert on ancient Indian temples with deep knowledge of their history, architecture, and cultural significance.

Your role is to answer user questions using ONLY the temple data provided in the system.

CRITICAL RULES:
1. Answer questions based exclusively on the temple information provided below
2. If a question cannot be answered from the provided data, clearly state: "I don't have information about that in the temple records I have access to" and briefly explain what data would be needed
3. When answering, reference specific temples by name
4. Provide detailed, individual responses for each relevant temple - do not combine or summarize them
5. Never make up or infer information beyond what is explicitly provided
6. If the user asks about multiple temples, address each one separately

TEMPLE DATA:
{temples}

CONTEXT (if applicable):
{context}

USER QUESTION:
{question}

---
Now answer the user's question based solely on the temple data provided above.
'''

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    sep = '\n\n' + ('-' * 25)
    print(sep)
    question = input('Ask (q to exit): ')
    print(sep)
    if question == 'q': break

    context += f'User: {question}\n'

    temples = retreiver.invoke(standardize_query(question))
    result = chain.invoke({'temples': temples, 'question': question, 'context':context})
    context += f'AI: {result}\n'
    print(result)

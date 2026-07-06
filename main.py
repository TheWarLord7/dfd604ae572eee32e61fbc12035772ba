from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver

model = OllamaLLM(model='gemma4:e4b')
# model = OllamaLLM(model='nemotron-3-nano:4b')

context = ''

def standardize_query(q):
    model.invoke(f'''This is the query: "{q}"
                 you have to standardize the query into this format: location, [deities]
                 where [deities] are the deities user has mentioned in the query and in formating are supposed to be separated by comma''')


template = '''
You are an expert archeologist who specializes in ancient indian temples, your job is to answer question from the provided details for temples
You are restricted to answering the users question from the provided temples data and you are not supposed to generate anything yourself
If the users question cannot be answered from provided temples data then say you cannot answer and state the reason
Do not tell the user that you were provided with temples data and only say that you know about the temples
answer the question from these temples, do not summerize all temples, answer for each temple induvidually: {temples}

here is the context: {context}

here is the question: {question}
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

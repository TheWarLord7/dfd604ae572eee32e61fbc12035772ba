from dotenv import load_dotenv
from vector import retreiver
import mysql.connector
import requests
import uuid
import json
import os


load_dotenv()
KEY = os.getenv('OPENROUTER')
KEY1 = os.getenv('OPENROUTER1')

class Connection:
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

    template1 = '''
    You are a semantic search and matching engine. Your job is to find the most relevant items from a provided array of data that best match a user's query.

    USER QUERY: {QUERY}

    DATA ARRAY:
    {DATA}

    OUTPUT FORMAT:
    Return only integer indices of the matched items separated by commas with no spaces. Return nothing else.

    MATCHING RULES:
    1. Analyze semantic meaning, not just keyword overlap
    2. Consider synonyms, related concepts, and contextual relevance
    3. Score matches based on how directly they address the user's intent
    4. Return results sorted by relevance in descending order
    5. Only include matches that meet or exceed the threshold
    6. Limit results to topK items (or fewer if fewer matches exceed threshold)

    EDGE CASES:
    - If no matches meet the threshold, return empty string
    - If data array is empty, return empty string
    - Handle various data types gracefully
    '''

    def __init__(self):
        self.start()

    def start(self):
        self.db = mysql.connector.connect(host='localhost', user='root',passwd='legacy',database='tpp')
        self.cursor = self.db.cursor()

    def get_identity(self):
        uid = str(uuid.uuid4())
        self.cursor.execute(f'CREATE TABLE {uid.replace('-','')}(message text, role varchar(6), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        self.db.commit()

        return uid

    def add_to_chat(self, _uuid, message, role):
        self.cursor.execute(f'INSERT INTO {_uuid.replace('-','')}(message, role) VALUES(%s, %s)', (message, role))
        self.db.commit()

    def get_context(self, _uuid, size=""):
        self.cursor.execute(f'SELECT MESSAGE, ROLE FROM {_uuid.replace('-','')} ORDER BY TIMESTAMP DESC{size}')
        return self.cursor.fetchall()

    def ask(self, _uuid, query):        
        temples = retreiver.invoke(query)
        context = ''
        # context = str(self.get_context(_uuid, " LIMIT 50"))

        # self.add_to_chat(_uuid, query, 'user')

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {KEY1}",
            },
            data=json.dumps({
                "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
                "messages": [
                {
                    "role": "system",
                    "content": self.template1.replace('{QUERY}',str(query)).replace('{DATA}', str(temples))
                }
                ]
            })
        )
        try:
            intarr = [int(i) for i in response.json()["choices"][0]["message"]["content"].split(',')]
            dataarr = [temples[i] for i in intarr]
            temples = dataarr
        except:
            pass

        while True:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {KEY}",
                },
                data=json.dumps({
                    "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
                    "messages": [
                    {
                        "role": "system",
                        "content": self.template.replace('{temples}',str(temples)).replace('{question}', query).replace('{context}', context)
                    }
                    ]
                })
            )
            try:
                res = response.json()["choices"][0]["message"]["content"]
                # self.add_to_chat(_uuid, res, 'AI')

                return res

            except:
                pass

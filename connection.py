from dotenv import load_dotenv
from vector import retreiver
import mysql.connector
import requests
import uuid
import json
import os


load_dotenv()
KEY = os.getenv('OPENROUTER')

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

    def __init__(self):
        self.start()

    def start(self):
        self.db = mysql.connector.connect(host='localhost', user='root',passwd='',database='tpp')
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
        context = str(self.get_context(_uuid, " LIMIT 50"))

        self.add_to_chat(_uuid, query, 'user')

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
                self.add_to_chat(_uuid, res, 'AI')

                return res

            except:
                pass

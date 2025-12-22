import os
from typing import Dict
import google.genai as genai
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))

def call_llm(query:str)->str:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents = query
    )
    return response.text

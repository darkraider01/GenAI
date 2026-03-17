import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

import time
from langchain_core.messages import BaseMessage

class ChatGroqWithRetry(ChatGroq):
    def invoke(self, *args, **kwargs):
        max_retries = 3
        retry_delay = 5
        for i in range(max_retries):
            try:
                return super().invoke(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) and i < max_retries - 1:
                    print(f"Rate limited. Retrying in {retry_delay}s... (Attempt {i+1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise e

def get_llm(model="llama-3.3-70b-versatile", temperature=0.6):
    """
    Creates a ChatGroq model using the generic llama-3.3-70b-versatile model.
    Includes simple retry logic for 429 Rate Limit errors.
    """
    primary_key = os.getenv("GROQ_API_KEY", "")
    
    return ChatGroqWithRetry(
        model=model,
        temperature=temperature,
        max_tokens=4096,
        api_key=primary_key,
        streaming=True
    )

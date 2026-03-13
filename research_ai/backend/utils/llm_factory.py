import os
from langchain_groq import ChatGroq

def get_llm(model="moonshotai/kimi-k2-instruct-0905", temperature=0.6):
    """
    Creates a ChatGroq model using the moonshotai/kimi-k2-instruct-0905 specified by the user.
    """
    return ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=4096,
        api_key=os.getenv("GROQ_API_KEY", "")
    )

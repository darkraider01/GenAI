import os
import json
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from utils.llm_factory import get_llm

class AssistantAgent:
    def __init__(self):
        self.system_prompt = """You are the ResearchNex AI Assistant.
You are an expert in AI-driven research platforms and the internal architecture of ResearchNex.
Your role is to explain how ResearchNex works, how hybrid retrieval operates, how research gap detection functions, and how the multi-agent research pipeline automates literature analysis.
Only answer questions related to ResearchNex, AI research automation, machine learning research workflows, and academic discovery tools.
If a user asks something unrelated to these topics, politely redirect them back to ResearchNex or AI research."""

    def is_query_relevant(self, query: str, llm) -> bool:
        # A lightweight check to see if we should refuse outright.
        # Alternatively, we just let the System Prompt handle it, which is usually robust enough for UI chatbots.
        # Given the requirements: "If a question is unrelated... the assistant should reply: 'I'm designed to assist with ResearchNex...'"
        # We can enforce this strictly via the system prompt instructions.
        pass

    async def stream_chat(self, messages_data: list, model_name: str):
        # Model mapping for Groq or others depending on string
        actual_model = model_name
        if model_name == "Gemini Pro": actual_model = "llama-3.3-70b-versatile"
        elif model_name == "GPT-4": actual_model = "llama-3.3-70b-versatile"
        elif model_name == "Claude": actual_model = "mixtral-8x7b-32768"
        else: actual_model = "llama-3.1-8b-instant"

        llm = get_llm(model=actual_model, temperature=0.7)
        
        # Format messages
        langchain_messages = [SystemMessage(content=self.system_prompt)]
        for msg in messages_data:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
                
        async def generate():
            try:
                # Use astream for Langchain ChatModels
                async for chunk in llm.astream(langchain_messages):
                    if chunk.content:
                        yield chunk.content
            except Exception as e:
                yield f"\n\n[Error: {str(e)}]"

        return StreamingResponse(generate(), media_type="text/event-stream")

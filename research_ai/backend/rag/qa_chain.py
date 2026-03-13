import os
from langchain_core.prompts import PromptTemplate
from backend.utils.llm_factory import get_llm
from backend.rag.retriever import ResearchRetriever

class QAChain:
    def __init__(self, retriever=None, llm=None):
        self.retriever = retriever or ResearchRetriever()
        
        # Assumes OPENAI_API_KEY is available in the environment
        self.llm = llm or get_llm(temperature=0)
        
        prompt_template = """
        You are an expert academic research assistant. Use the following retrieved research papers to answer the user's question.
        If the answer is not contained in the papers, say that you cannot answer based on the provided literature.
        Always cite the papers you use by their title and authors.

        Context Papers:
        {context}

        Question: {question}

        Answer:
        """
        
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        self.chain = self.prompt | self.llm
        
    def answer(self, question: str, top_k: int = 5):
        papers = self.retriever.retrieve(question, top_k=top_k)
        
        context_parts = []
        for i, p in enumerate(papers):
            context_parts.append(
                f"[Paper {i+1}] Title: {p['title']}\nAuthors: {p['authors']}\nYear: {p['year']}\nAbstract: {p['abstract']}\n"
            )
        
        context_str = "\n".join(context_parts)
        
        response = self.chain.invoke({
            "context": context_str,
            "question": question
        })
        
        return {
            "answer": response.content,
            "source_papers": papers
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    qa = QAChain()
    print(qa.answer("What are the latest advancements in cross-silo federated learning?"))

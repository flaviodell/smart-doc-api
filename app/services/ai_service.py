from groq import Groq
from ..core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

class AIService:
    @staticmethod
    def process_task(task: str, text: str, question: str = None):
        if task == "summarize":
            prompt = f"Summarize the following text briefly:\n\n{text}"
        elif task == "classify":
            prompt = f"Classify the sentiment or category of this text in one word:\n\n{text}"
        elif task == "qa":
            prompt = f"Context: {text}\n\nQuestion: {question}\n\nAnswer concisely."
        else:
            return "Invalid task"

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        
        return completion.choices[0].message.content
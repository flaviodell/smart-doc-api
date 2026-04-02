from groq import Groq
from ..core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

GROQ_MODEL = "llama-3.1-8b-instant"


class AIService:
    @staticmethod
    def process_task(task: str, text: str, question: str = None) -> tuple[str, str]:
        if task == "classify":
            prompt = (
                f"Classify the following text into exactly one of these categories: "
                f"tecnologia, scienza, sport, economia, politica.\n\n"
                f"Text: {text}\n\n"
                f"Respond with only the category name in Italian, nothing else."
            )
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            label = completion.choices[0].message.content.strip().lower()
            return f"Categoria: {label}", GROQ_MODEL

        elif task == "summarize":
            prompt = f"Summarize the following text briefly:\n\n{text}"

        elif task == "qa":
            if not question:
                return "Per il task 'qa' è necessario fornire il campo 'question'.", GROQ_MODEL
            prompt = f"Context: {text}\n\nQuestion: {question}\n\nAnswer concisely."

        else:
            return "Task non supportato. Scegli tra: summarize, qa, classify.", "none"

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return completion.choices[0].message.content, GROQ_MODEL
    
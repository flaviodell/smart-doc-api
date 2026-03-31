from groq import Groq
from transformers import pipeline
from ..core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

# HuggingFace pipeline
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

class AIService:
    @staticmethod
    def process_task(task: str, text: str, question: str = None):
        
        if task == "classify":
            candidate_labels = ["tecnologia", "scienza", "sport", "economia", "politica"]
            result = classifier(text, candidate_labels)
            
            best_label = result['labels'][0]
            confidence = result['scores'][0]
            return f"Categoria: {best_label} (Confidenza: {confidence:.2f})"
        
        elif task == "summarize":
            prompt = f"Summarize the following text briefly:\n\n{text}"
        elif task == "qa":
            prompt = f"Context: {text}\n\nQuestion: {question}\n\nAnswer concisely."
        else:
            return "Task non supportato. Scegli tra: summarize, qa, classify."

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return completion.choices[0].message.content
    
import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class AnswerGenerator:
    """
    Generates answers using Gemini as primary and Groq as backup.
    """

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

    def build_prompt(self, question, chunks):
        """
        Build prompt with question and retrieved chunks.
        """
        context = ""
        for i, chunk in enumerate(chunks):
            context += f"\n\nSource {i+1}: {chunk['source']}\n{chunk['text']}"

        prompt = f"""You are a helpful assistant. Answer the question using ONLY the content provided below.
If the answer is not in the content, say "I could not find this information in the provided content."

Content:
{context}

Question: {question}

Give a clear and accurate answer. Mention which source the information came from."""

        return prompt

    def generate(self, question, chunks):
        """
        Generate answer using Gemini first, Groq as backup.
        """
        prompt = self.build_prompt(question, chunks)

        # Try Gemini first
        try:
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return {
                "answer": response.text,
                "model_used": "Gemini"
            }

        except Exception as e:
            print(f"Gemini failed: {e}. Switching to Groq...")

        # Backup - Try Groq
        try:
            client = Groq(api_key=self.groq_key)
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "answer": response.choices[0].message.content,
                "model_used": "Groq"
            }

        except Exception as e:
            return {
                "answer": "Both AI services are unavailable. Please try again later.",
                "model_used": "None"
            }
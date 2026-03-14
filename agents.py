import openai

class ResearchAgents:
    def __init__(self, api_key):
        # We point the "base_url" to Groq instead of OpenAI
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def summarize_paper(self, abstract):
        # We use a Groq model name like 'llama-3.3-70b-versatile'
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Summarize this: {abstract}"}]
        )
        return response.choices[0].message.content

    def analyze_trends(self, summaries):
        combined_text = "\n---\n".join(summaries)
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Find trends in this: {combined_text}"}]
        )
        return response.choices[0].message.content
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20240620" # Using the latest available stable model if not specified otherwise

    def message(self, system_prompt: str, user_content: str, max_tokens: int = 4000):
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_content}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return None

def test_claude():
    client = ClaudeClient()
    response = client.message("You are a helpful assistant.", "Hello, Claude!")
    print(response)

if __name__ == "__main__":
    test_claude()

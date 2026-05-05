from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from backend.utils.github_client import GitHubClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ContextCollector:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        self.github = GitHubClient()

    def collect_context(self, pr_url: str, diff: str) -> dict:
        repo_url = "/".join(pr_url.split("/")[:-2])
        tree = self.github.fetch_repo_tree(repo_url)
        file_tree = "\n".join([f["path"] for f in tree if f["type"] == "blob"])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a repository context analyst. Given a PR diff and repo structure,
            identify:
            1. Related files that might be affected (via imports/call graph)
            2. Architecture documentation that defines behavioral contracts (README, ARCHITECTURE.md, etc.)
            3. Relevant past commits that touched the same files
            
            Output as JSON:
            {{
              "related_files": ["path/to/file.ts", ...],
              "architecture_docs": ["ARCHITECTURE.md", "ADR-002.md", ...],
              "past_commits": ["abc123", "def456", ...]
            }}"""),
            ("user", "PR Diff:\n{diff}\n\nRepo File Tree:\n{file_tree}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"diff": diff, "file_tree": file_tree})
        
        try:
            content = response.content
            if isinstance(content, str):
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                context_map = json.loads(content)
            else:
                # Handle cases where response might be different or have parts
                context_map = {"related_files": [], "architecture_docs": [], "past_commits": []}
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            context_map = {"related_files": [], "architecture_docs": [], "past_commits": []}

        related_content = {}
        for path in context_map.get("related_files", []) + context_map.get("architecture_docs", []):
            content = self.github.fetch_file_content(repo_url, path)
            if content:
                related_content[path] = content

        return {
            "context_map": context_map,
            "related_content": related_content
        }

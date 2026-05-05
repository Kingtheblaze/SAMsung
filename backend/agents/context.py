from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from backend.utils.github_client import GitHubClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ContextCollector:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
        self.github = GitHubClient()

    def collect_context(self, pr_url: str, diff: str) -> dict:
        """
        Builds the repo context map: README, architecture docs, related files.
        """
        # 1. Fetch repo file tree
        # Extract repo_url from pr_url (e.g., https://api.github.com/repos/owner/repo/pulls/1)
        repo_url = "/".join(pr_url.split("/")[:-2])
        tree = self.github.fetch_repo_tree(repo_url)
        file_tree = "\n".join([f["path"] for f in tree if f["type"] == "blob"])

        # 2. Identify related files via LLM
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
            # Clean up the response if it contains markdown formatting
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            context_map = json.loads(content)
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            context_map = {"related_files": [], "architecture_docs": [], "past_commits": []}

        # 3. Fetch content of related files + docs
        related_content = {}
        for path in context_map.get("related_files", []) + context_map.get("architecture_docs", []):
            content = self.github.fetch_file_content(repo_url, path)
            if content:
                related_content[path] = content

        return {
            "context_map": context_map,
            "related_content": related_content
        }

if __name__ == "__main__":
    # Test with a dummy PR
    # collector = ContextCollector()
    # print(collector.collect_context("https://api.github.com/repos/octocat/Hello-World/pulls/1347", "dummy diff"))
    pass

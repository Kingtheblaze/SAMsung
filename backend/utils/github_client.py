import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.token else {}

    def fetch_pr_diff(self, pr_url: str):
        """Fetches the diff for a given PR URL."""
        diff_url = f"{pr_url}.diff"
        resp = requests.get(diff_url, headers=self.headers)
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"Error fetching diff: {resp.status_code} - {resp.text}")
            return None

    def fetch_repo_tree(self, repo_url: str, recursive: bool = True):
        """Fetches the repository file tree."""
        # repo_url usually looks like https://api.github.com/repos/owner/repo
        tree_url = f"{repo_url}/git/trees/main?recursive={1 if recursive else 0}"
        resp = requests.get(tree_url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json().get("tree", [])
        else:
            print(f"Error fetching tree: {resp.status_code} - {resp.text}")
            return []

    def fetch_file_content(self, repo_url: str, path: str):
        """Fetches the content of a file at a specific path."""
        content_url = f"{repo_url}/contents/{path}"
        resp = requests.get(content_url, headers=self.headers)
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return content
        else:
            print(f"Error fetching file {path}: {resp.status_code} - {resp.text}")
            return None

    def post_comment(self, pr_url: str, body: str, path: str = None, line: int = None):
        """Posts a comment to a PR. If path and line are provided, it's an inline comment."""
        if path and line:
            # Inline comment requires a commit_id and position
            # This is more complex, might need to fetch PR details first
            comments_url = f"{pr_url}/comments"
            # For simplicity in hackathon, we might just post to the PR discussion if inline is tricky
            # But let's try to stick to the plan
            pass
        else:
            comments_url = f"{pr_url}/reviews"
            payload = {
                "body": body,
                "event": "COMMENT"
            }
            resp = requests.post(comments_url, json=payload, headers=self.headers)
            return resp.status_code == 201

# Example usage
if __name__ == "__main__":
    client = GitHubClient()
    # print(client.fetch_pr_diff("https://api.github.com/repos/octocat/Hello-World/pulls/1347"))

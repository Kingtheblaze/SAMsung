# GitHub API & Diff Fetching Guide

This document explains how ContextDiff interacts with GitHub to fetch Pull Request data and how to authenticate your requests.

## 1. Authentication

GitHub API requests are authenticated using a **Personal Access Token (PAT)**.

### How to get a token:
1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens).
2. Click **Generate new token**.
3. Select the following scopes:
   - `repo` (Full control of private repositories - required if reviewing private repos)
   - `pull_requests:read` (Required to fetch PR diffs)
   - `pull_requests:write` (Required to post inline comments)
4. Copy the token and add it to your `backend/.env` file:
   ```env
   GITHUB_TOKEN=ghp_your_secret_token_here
   ```

## 2. Fetching the PR Diff

We fetch the PR diff by appending `.diff` to the PR URL or using the specialized `Accept` header.

### Implementation Detail
In `backend/utils/github_client.py`, we use the following logic:

```python
def fetch_pr_diff(self, pr_url: str):
    # pr_url example: https://api.github.com/repos/owner/repo/pulls/1
    diff_url = f"{pr_url}.diff" 
    resp = requests.get(diff_url, headers=self.headers)
    return resp.text
```

GitHub automatically serves the raw patch/diff content when you append `.diff` to a PR URL, making it easy for our **Diff Analyzer** agent to process the changes.

## 3. Fetching Repository Context

To understand the "why" behind the code, we fetch the repository's file tree and specific files like `README.md`.

### Fetching the Tree
```python
# Fetches the entire repository structure recursively
tree_url = f"{repo_url}/git/trees/main?recursive=1"
resp = requests.get(tree_url, headers=self.headers)
```

### Fetching File Content
Files are returned as Base64 encoded strings from the GitHub API. We decode them to get the raw source code:
```python
content = base64.b64decode(data['content']).decode('utf-8')
```

## 4. Posting Comments

To post an inline comment on a specific line of the diff, we send a POST request to the PR's review comments endpoint.

```python
comments_url = f"{pr_url}/comments"
payload = {
    "body": "Your AI review comment here",
    "path": "path/to/file.py",
    "line": 142,
    "side": "RIGHT" # Refers to the 'new' version of the code
}
requests.post(comments_url, json=payload, headers=self.headers)
```

> [!TIP]
> Always use `side: "RIGHT"` for comments on the new code in the PR to ensure they appear correctly on the changed lines.

from langchain_community.vectorstores import Chroma
from langchain_anthropic import AnthropicEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
import json
import os
from dotenv import load_dotenv

load_dotenv()

class SecurityAuditor:
    def __init__(self):
        self.embeddings = AnthropicEmbeddings()
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
        self.db_path = "./chroma_db"
        self.kb = self._setup_kb()

    def _setup_kb(self):
        # In a real app, this would persist and only load if exists
        owasp_docs = [
            "A01: Broken Access Control - Failure to enforce restrictions on what authenticated users can do.",
            "A02: Cryptographic Failures - Weaknesses in data encryption, often leading to sensitive data exposure.",
            "A03: Injection - Sending untrusted data as part of a command or query (e.g., SQL, NoSQL).",
            "A04: Insecure Design - Risks related to design and architectural flaws.",
            "A05: Security Misconfiguration - Insecure default configurations or incomplete configurations.",
            "A06: Vulnerable and Outdated Components - Using software with known vulnerabilities.",
            "A07: Identification and Authentication Failures - Weaknesses in user identity confirmation.",
            "A08: Software and Data Integrity Failures - Assumptions made about software updates or data without verification.",
            "A09: Security Logging and Monitoring Failures - Insufficient logging to detect or respond to breaches.",
            "A10: Server-Side Request Forgery (SSRF) - Forcing the server to make requests to unintended locations."
        ]
        
        if not os.path.exists(self.db_path):
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.create_documents(owasp_docs)
            vectorstore = Chroma.from_documents(chunks, self.embeddings, persist_directory=self.db_path)
            return vectorstore
        else:
            return Chroma(persist_directory=self.db_path, embedding_function=self.embeddings)

    def audit_security(self, diff: str) -> list:
        """
        Maps changes to OWASP Top 10 using RAG.
        """
        # 1. RAG: Retrieve relevant OWASP docs
        query = f"Security vulnerabilities related to: {diff[:500]}"
        docs = self.kb.similarity_search(query, k=3)
        owasp_context = "\n\n".join([d.page_content for d in docs])

        # 2. Ask Claude to analyze
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a security auditor. Given:
            1. A code diff
            2. Relevant OWASP vulnerability descriptions (from RAG)
            
            Flag security risks with:
            - OWASP category (A01-A10)
            - Confidence score (0-100)
            - Suggested remediation
            
            Output as JSON list:
            {{
              "severity": "CRITICAL|HIGH|MEDIUM|LOW",
              "confidence": 0-100,
              "category": "OWASP-A03:Injection",
              "file": "src/api/user.ts",
              "line": 142,
              "message": "Raw user input passed to SQL query without sanitization.",
              "fix": "Use parameterized queries or ORM."
            }}"""),
            ("user", "Diff:\n{diff}\n\nOWASP Context:\n{owasp_context}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"diff": diff, "owasp_context": owasp_context})

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            findings = json.loads(content)
            if not isinstance(findings, list):
                findings = [findings]
        except Exception as e:
            print(f"Error parsing SecurityAuditor response: {e}")
            findings = []

        return findings

if __name__ == "__main__":
    # auditor = SecurityAuditor()
    # print(auditor.audit_security("dummy diff with sql query"))
    pass

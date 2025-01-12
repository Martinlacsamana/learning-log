''' STAGE 2: COMMIT CLASSIFICATION '''

from openai import OpenAI
import os

COMMIT_TYPES = {
    'FEATURE': 'New feature or functionality addition',
    'BUGFIX': 'Bug fixes and corrections',
    'REFACTOR': 'Code restructuring without behavior change',
    'TEST': 'Adding or modifying tests',
    'DOCS': 'Documentation updates',
    'INTEGRATION': 'External service/API integration',
    'STYLE': 'Code style/formatting changes',
    'PERF': 'Performance improvements',
    'DEPS': 'Dependency updates'
}

class CommitClassifier:
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def __init__(self):
        self.client = OpenAI()

    def classify_commit(self, commit_message, code_changes):
        """Classify commit using OpenAI"""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a code commit classifier."},
                    {"role": "user", "content": f"Classify: {commit_message}\nChanges: {code_changes}\nCategories: {COMMIT_TYPES}"}
                ],
                max_tokens=50,
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content.strip()['type']
        except Exception:
            return "UNKNOWN" 
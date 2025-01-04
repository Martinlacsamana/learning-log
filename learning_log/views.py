from datetime import datetime
from github import Github, Auth
from openai import OpenAI
import os
from .models import db, LearningLog

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

def fetch_github_commits(username=None, since=None):
    """Fetch commits from GitHub"""
    token = os.getenv('GITHUB_TOKEN')
    g = Github(auth=Auth.Token(token))
    user = g.get_user(username) if username else g.get_user()
    
    commits_data = []
    for repo in user.get_repos():
        for commit in repo.get_commits(author=user.login):
            file_changes = [{
                'filename': f.filename,
                'additions': f.additions,
                'deletions': f.deletions,
                'changes': f.patch
            } for f in commit.files]
            
            commits_data.append({
                'commit_hash': commit.sha,
                'commit_message': commit.commit.message,
                'commit_date': commit.commit.author.date.isoformat(),
                'repository': repo.name,
                'files_changed': file_changes
            })
    
    return commits_data

def store_learning_log(commit_data):
    """Store a single learning log entry"""
    try:
        if LearningLog.find_by_commit_hash(commit_data['commit_hash']):
            return False

        LearningLog.create({
            'commit_hash': commit_data['commit_hash'],
            'commit_message': commit_data['commit_message'],
            'commit_date': datetime.fromisoformat(commit_data['commit_date'].replace('Z', '+00:00')),
            'repository': commit_data['repository'],
            'lines_added': sum(f['additions'] for f in commit_data['files_changed']),
            'lines_deleted': sum(f['deletions'] for f in commit_data['files_changed']),
            'files_changed': commit_data['files_changed']
        })
        return True
    except Exception as e:
        print(f"Error storing log: {e}")
        return False

def classify_commit(commit_message, code_changes):
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
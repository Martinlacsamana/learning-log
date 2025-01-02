from github import Github, GithubIntegration, Auth
import os
import logging
from pprint import pprint  # for better debug output

logger = logging.getLogger(__name__)

def fetch_github_commits(username=None, since=None):
    """
    Fetch commits from GitHub for a given username
    """
    token = os.getenv('GITHUB_TOKEN')
    print(f"Token found: {'Yes' if token else 'No'}")
    
    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
        
        try:
            authenticated_user = g.get_user()
            print(f"Authenticated as: {authenticated_user.login}")
            
            user = g.get_user(username) if username else g.get_user()
            
            commits_data = []
            for repo in user.get_repos():
                try:
                    print(f"\nChecking repo: {repo.name}")
                    commits = repo.get_commits(author=user.login)
                    
                    for commit in commits:
                        try:
                            # get the code changes from each file
                            file_changes = []
                            for file in commit.raw_data.get('files', []):
                                file_changes.append({
                                    'filename': file.get('filename'),
                                    'additions': file.get('additions', 0),
                                    'deletions': file.get('deletions', 0),
                                    'changes': file.get('patch', '')  # the actual code diff
                                })

                            commit_data = {
                                'commit_hash': commit.sha,
                                'commit_message': commit.raw_data['commit']['message'],
                                'commit_date': commit.raw_data['commit']['author']['date'],
                                'repository': repo.name,
                                'author_name': commit.raw_data['commit']['author']['name'],
                                'files_changed': file_changes
                            }
                            commits_data.append(commit_data)
                            
                        except (KeyError, AttributeError) as e:
                            print(f"Error accessing commit data: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error fetching commits from {repo.name}: {str(e)}")
                    continue
            
            print(f"\nTotal commits found: {len(commits_data)}")
            return commits_data
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return {"error": f"GitHub authentication failed: {str(e)}"}
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return {"error": str(e)} 
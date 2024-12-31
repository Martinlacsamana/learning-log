from github import Github
import os

def fetch_github_commits(username=None, since=None):
    """
    Fetch commits from GitHub for a given username
    """
    # initialize github client with personal access token
    g = Github(os.getenv('GITHUB_TOKEN'))
    
    # get the user
    user = g.get_user(username) if username else g.get_user()
    
    commits_data = []
    # fetch all repositories
    for repo in user.get_repos():
        try:
            # get commits for each repo
            commits = repo.get_commits(author=user.login, since=since)
            for commit in commits:
                commits_data.append({
                    'commit_hash': commit.sha,
                    'commit_message': commit.commit.message,
                    'commit_date': commit.commit.author.date,
                    'repository': repo.name
                })
        except Exception as e:
            # skip repos where we don't have access or other issues
            print(f"Error fetching commits from {repo.name}: {str(e)}")
            continue
    
    return commits_data 
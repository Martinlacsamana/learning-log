from github import Github, GithubIntegration, Auth
import os
import logging
from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env file

logger = logging.getLogger(__name__)

def fetch_github_commits(username=None, since=None):
    """
    Fetch commits from GitHub for a given username
    """
    token = os.getenv('GITHUB_TOKEN')
    print(f"Token found: {'Yes' if token else 'No'}") 
    if not token:
        logger.error("No GITHUB_TOKEN found in environment variables")
        return {"error": "GitHub token not configured"}
    
    try:
        # initialize github client with token using the new Auth approach
        auth = Auth.Token(token)
        g = Github(auth=auth)
        
        # test the authentication
        try:
            g.get_user().login
        except Exception as e:
            logger.error(f"GitHub authentication failed: {str(e)}")
            return {"error": "GitHub authentication failed"}
        
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
                logger.error(f"Error fetching commits from {repo.name}: {str(e)}")
                continue
        
        return commits_data
        
    except Exception as e:
        logger.error(f"Error in fetch_github_commits: {str(e)}")
        return {"error": str(e)} 
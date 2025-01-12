# Learning Log Service 📚

A service that tracks and analyzes GitHub commits to create a learning log with AI-powered insights. This service connects to GitHub's API to extract commit history, stores it in MongoDB, and uses OpenAI to classify and analyze commit patterns. It's designed to help developers track their learning journey through their coding activities.

## 🏗️ Architecture

The system operates in several stages:

### Stage 1: Commit Extraction & Storage
- Fetches commit history from GitHub API
- Extracts commit messages, changes, and metadata
- Stores structured data in MongoDB
- Prevents duplicate entries through commit hash checking

### Stage 2: AI Classification
- Processes stored commits through OpenAI's API
- Classifies commits into categories:
  - FEATURE: New feature or functionality
  - BUGFIX: Bug fixes and corrections
  - REFACTOR: Code restructuring
  - TEST: Test additions/modifications
  - DOCS: Documentation updates
  - And more...
- Updates classification fields in MongoDB

### Stage 3: Real-time Updates
- GitHub webhook integration
- Automatic processing of new commits
- Immediate classification and storage

### Stage 4: Maintenance
- Scheduled tasks for pending classifications
- Database cleanup and optimization
- Error handling and retries

### Stage 5: API Integration
- RESTful endpoints for external access
- Integration with personal website
- Filtered and sorted commit history access

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.8+)
- **Database**: MongoDB
- **AI Integration**: OpenAI GPT-3.5
- **GitHub Integration**: PyGithub
- **Dependencies**: See `requirements.txt` for full list

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- MongoDB
- GitHub Account
- OpenAI API Key

### Installation Steps

1. Clone and setup environment:
```bash```
```git clone https://github.com/yourusername/learning-log.git```
```cd learning-log```
```python -m venv venv```
```source venv/bin/activate # On Windows: venv\Scripts\activate```
```pip install -r requirements.txt```

2. Configure environment:
```bash```
```cp .env.example .env```

3. Set required variables in `.env`:
```bash```
```GITHUB_TOKEN=your_github_token```
```OPENAI_API_KEY=your_openai_key```
```MONGODB_URL=mongodb://localhost:27017/learning_log```

4. Run the application:
```bash```
```python run.py```



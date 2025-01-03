from app import openai_client, db
from app.models.learning_log import LearningLog

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

def classify_commit(commit_message, code_changes):
    """
    Use OpenAI to classify the commit type based on commit message and code changes
    """
    try:
        prompt = f"""
        Analyze this commit and classify it into exactly one category.

        Commit Message: {commit_message}
        Code Changes: {code_changes}

        Available categories:
        {COMMIT_TYPES}

        Return the classification as a JSON object with a single key 'type' whose value must be one of: 
        {list(COMMIT_TYPES.keys())}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a code commit classifier.
                Analyze commits and return ONLY a JSON object with the classification.
                Be decisive and choose the best matching category."""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.3,
            response_format={ "type": "json_object" }  # enforce JSON response
        )
        
        # Parse the JSON response
        classification = response.choices[0].message.content.strip()
        return classification['type']
        
    except Exception as e:
        print(f"Error classifying commit: {str(e)}")
        return "UNKNOWN"

def batch_classify_commits():
    """
    Iterate through all learning logs without a commit_type and classify them
    """
    try:
        # Get all logs that don't have a commit_type
        unclassified_logs = LearningLog.query.filter_by(commit_type=None).all()
        
        processed = 0
        failed = 0
        
        for log in unclassified_logs:
            try:
                # Prepare code changes summary
                code_summary = ""
                if log.files_changed:  # assuming this is stored as JSON
                    changes = log.files_changed
                    code_summary = f"Files modified: {len(changes)} "
                    code_summary += f"Additions: {sum(f['additions'] for f in changes)} "
                    code_summary += f"Deletions: {sum(f['deletions'] for f in changes)}"
                
                # Get classification
                commit_type = classify_commit(log.commit_message, code_summary)
                
                # Update the log
                log.commit_type = commit_type
                processed += 1
                
            except Exception as e:
                print(f"Error processing log {log.id}: {str(e)}")
                failed += 1
                continue
        
        # Commit all changes
        db.session.commit()
        
        return {
            "processed": processed,
            "failed": failed,
            "total": len(unclassified_logs)
        }
        
    except Exception as e:
        print(f"Error in batch classification: {str(e)}")
        db.session.rollback()
        return {
            "error": str(e),
            "processed": 0,
            "failed": 0,
            "total": 0
        } 
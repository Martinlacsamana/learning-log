''' STAGE 2: COMMIT CLASSIFICATION '''

from openai import OpenAI
import os
import logging
from learning_log.models import LearningLog

COMMIT_TYPES = {
    1: 'New feature or functionality addition',
    2: 'Bug fixes and corrections',
    3: 'Code restructuring without behavior change',
    4: 'Adding or modifying tests',
    5: 'Documentation updates',
    6: 'External service/API integration',
    7: 'Code style/formatting changes',
    8: 'Performance improvements',
    9: 'Dependency updates'
}

logger = logging.getLogger(__name__)

class CommitClassifier:
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def __init__(self):
        self.client = OpenAI()

    def classify_commit(self, commit_message):
        """Classify commit using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a commit classifier. Respond with a number 1-9 based on the commit type."},
                    {"role": "user", "content": f"""
                        Classify this commit message into one of these types:
                        1: Feature - New functionality
                        2: Bugfix - Bug fixes
                        3: Refactor - Code restructuring
                        4: Test - Testing changes
                        5: Docs - Documentation
                        6: Integration - External services
                        7: Style - Formatting
                        8: Performance - Optimizations
                        9: Dependencies - Package updates

                        Commit message: {commit_message}

                        Respond with a JSON object containing only a 'type' field with a number 1-9."""}
                ],
                max_tokens=20,  # need very few tokens now
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            type_num = response.choices[0].message.content.strip()['type']
            return COMMIT_TYPES[type_num]
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return "UNKNOWN"

    def test_classification(self, limit=15):
        """Test classification on a few commits without storing results"""
        logger.info(f"Testing classification with {limit} commits...")
        results = []
        
        # Get some unclassified commits
        unclassified = LearningLog.find_unclassified(limit=limit)
        
        for commit in unclassified:
            predicted_type = self.classify_commit(commit['commit_message'])
            results.append({
                'commit_hash': commit['commit_hash'],
                'commit_message': commit['commit_message'],
                'predicted_type': predicted_type
            })
            logger.info(f"Classified '{commit['commit_message'][:50]}...' as {predicted_type}")
        
        return results 
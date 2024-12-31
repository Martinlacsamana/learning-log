from app import openai_client

def generate_commit_summary(commit_message, repository):
    """
    Generate a technical learning summary from a commit using OpenAI
    """
    try:
        prompt = f"""
        Repository: {repository}
        Commit Message: {commit_message}

        Generate a concise technical learning summary that:
        1. Focuses on the technical skills or concepts demonstrated
        2. Highlights any new technologies or patterns used
        3. Describes the problem solved or feature implemented
        
        Keep it brief and focused on the learning aspect.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a technical mentor who helps developers track their learning progress.
                Format your responses as concise technical learning points. Focus on skills gained, technologies used, and problems solved."""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return "Failed to generate summary" 
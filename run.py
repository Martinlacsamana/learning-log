import sys
sys.dont_write_bytecode = True

from pathlib import Path
import os
from dotenv import load_dotenv

# Force load the specific .env file
base_dir = Path(__file__).parent
env_path = base_dir / '.env'

# Clear any existing env vars first
if 'GITHUB_TOKEN' in os.environ:
    del os.environ['GITHUB_TOKEN']

# Load the .env file
load_dotenv(env_path, override=True)  # force override any existing vars

# Debug verification
token = os.getenv('GITHUB_TOKEN')
print(f"Loaded token starts with: {token[:10] if token else 'None'}")

from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 
import sys
sys.dont_write_bytecode = True

from pathlib import Path
import os
from dotenv import load_dotenv

# Force load the specific .env file
base_dir = Path(__file__).parent
env_path = base_dir / '.env'
load_dotenv(env_path, override=True)

from learning_log import app

if __name__ == '__main__':
    app.run(debug=True) 
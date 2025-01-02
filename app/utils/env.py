from dotenv import load_dotenv
from pathlib import Path

def init_env():
    env_path = Path(__file__).parents[2] / '.env'
    load_dotenv(env_path)

import sys
import os

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Set environment variable
os.environ['PYTHONANYWHERE_DOMAIN'] = 'griffinstrier.pythonanywhere.com'

# Import your Flask app
from src.web_app import app as application
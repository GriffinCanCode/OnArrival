import sys
import os

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Set environment variable for PythonAnywhere domain if not already set
if 'PYTHONANYWHERE_DOMAIN' not in os.environ:
    # Use a placeholder that should be configured in production
    os.environ['PYTHONANYWHERE_DOMAIN'] = 'your-domain.pythonanywhere.com'

# Import your Flask app
from src.web_app import app as application
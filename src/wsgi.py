import sys
import os

# Add your project directory to Python path
path = '/home/griffinstrier/projects/onarrival'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable
os.environ['PYTHONANYWHERE_DOMAIN'] = 'griffinstrier.pythonanywhere.com'

# Import your Flask app
from web_app import app as application 
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Set environment variable
os.environ['PYTHONANYWHERE_DOMAIN'] = 'greyhatharold.pythonanywhere.com'

# Import your Flask app
try:
    from src.web_app import app as application
    print("Successfully imported application from src.web_app")
except Exception as e:
    print(f"Error importing application: {str(e)}")
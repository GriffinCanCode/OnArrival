import sys
import os

# Add the project root directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set environment variable
os.environ['PYTHONANYWHERE_DOMAIN'] = 'greyhatharold.pythonanywhere.com'

# Import your Flask app
try:
    from src.web_app import app as application
    print("Successfully imported application from src.web_app")
except Exception as e:
    import traceback
    print(f"Error importing application: {str(e)}")
    print("Traceback:")
    print(traceback.format_exc())
import sys
import os

# Add project root and src directories to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_dir, 'src')

# Add only the src directory to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)  # Insert at beginning to ensure it's checked first

# Create static and templates directories if they don't exist
static_dir = os.path.join(src_dir, 'static')
templates_dir = os.path.join(src_dir, 'templates')
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Set environment variable
os.environ['PYTHONANYWHERE_DOMAIN'] = 'greyhatharold.pythonanywhere.com'

# Import your Flask app
try:
    from src.web_app import app  # Changed to import directly from web_app
    application = app
    print("Successfully imported application from web_app")
except Exception as e:
    import traceback
    print(f"Error importing application: {str(e)}")
    print("Traceback:")
    print(traceback.format_exc())
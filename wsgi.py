import sys
import os

# Add project root and src directories to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_dir, 'src')
services_dir = os.path.join(src_dir, 'services')
static_dir = os.path.join(src_dir, 'static')
templates_dir = os.path.join(src_dir, 'templates')

for path in [project_dir, src_dir, services_dir]:
    if path not in sys.path:
        sys.path.append(path)

# Create static and templates directories if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Set environment variable
os.environ['PYTHONANYWHERE_DOMAIN'] = 'greyhatharold.pythonanywhere.com'

# Import your Flask app
try:
    from src.web_app import app
    application = app  # This line is crucial - WSGI looks for 'application'
    print("Successfully imported application from src.web_app")
except Exception as e:
    import traceback
    print(f"Error importing application: {str(e)}")
    print("Traceback:")
    print(traceback.format_exc())
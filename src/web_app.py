from flask import Flask, render_template, jsonify, request, send_from_directory
from services.location_alert_system import LocationAlertSystem
import threading
import os

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)
alert_system = LocationAlertSystem()

# Configure for PythonAnywhere
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    app.config.update(
        SERVER_NAME=os.getenv('PYTHONANYWHERE_DOMAIN'),
        PREFERRED_URL_SCHEME='https'
    )

# Start the notification service in a separate thread
flask_thread = threading.Thread(target=alert_system.notification_service.run, daemon=True)
flask_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/groups', methods=['GET'])
def get_groups():
    groups = alert_system.contact_storage.load_groups()
    return jsonify([{
        'name': group.name,
        'contacts': [{'name': c.name, 'phone': c.phone} for c in group.contacts]
    } for group in groups])

@app.route('/api/send_business', methods=['POST'])
def send_business_alert():
    data = request.json
    try:
        alert_system.notification_service.make_call(
            data['phone'],
            data['message'],
            data['business_name']
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/send_leisure', methods=['POST'])
def send_leisure_alert():
    data = request.json
    try:
        groups = alert_system.contact_storage.load_groups()
        group = next((g for g in groups if g.name == data['group']), None)
        
        if not group:
            return jsonify({'success': False, 'error': 'Group not found'})

        message_template = data['message']
        for contact in group.contacts:
            message = message_template.replace('()', contact.name)
            alert_system.notification_service.make_call(
                contact.phone,
                message,
                include_follow_up=True
            )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/icon.png')
def serve_icon():
    return send_from_directory('static', 'icon.png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
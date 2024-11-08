from flask import Flask, render_template, jsonify, request
from services.location_alert_system import LocationAlertSystem
from services.notification_service import NotificationService
import os

app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

alert_system = LocationAlertSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send_alert', methods=['POST'])
def send_alert():
    data = request.json
    try:
        alert_system.notification_service.make_call(
            data['phone'],
            data['message'],
            data.get('business_name')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
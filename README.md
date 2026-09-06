# OnArrival

A location-based notification system that automatically sends voice calls and text messages to contacts when you arrive at specific destinations. Perfect for letting friends, family, or business contacts know when you've safely reached your destination.

## Features

### 🎯 Core Functionality
- **Automated Voice Calls**: Send pre-recorded or custom voice messages via Twilio
- **Location-Based Alerts**: Trigger notifications based on GPS coordinates and radius
- **Contact Management**: Organize contacts into groups for easy notification management
- **Multi-Interface Support**: Web app and desktop GUI (PyQt6) interfaces
- **Business & Leisure Modes**: Different notification templates for different contexts

### 📱 Web Interface
- Mobile-responsive design with iOS PWA support
- Business alert system for professional notifications
- Leisure alerts for personal contacts
- Contact and group management
- Custom message templates with humorous pre-built options

### 🖥️ Desktop Application
- PyQt6-based GUI for desktop users
- Full contact and location management
- Real-time location monitoring

## Technology Stack

- **Backend**: Python 3.12, Flask
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **GUI Framework**: PyQt6
- **Voice/SMS Service**: Twilio API
- **Location Services**: GeoPy, geographiclib
- **Deployment**: Gunicorn WSGI server, ngrok for development
- **Data Storage**: JSON files for contacts and groups

## Installation

### Prerequisites
- Python 3.12+
- Twilio account with phone number
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd OnArrival
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   PYTHONANYWHERE_DOMAIN=your_domain.pythonanywhere.com  # Optional
   ```

## Usage

### Web Application

1. **Start the web server**:
   ```bash
   python wsgi.py
   ```

2. **Access the interface**:
   - Open your browser to `http://localhost:5000`
   - For mobile testing, use ngrok tunnel (configured automatically)

3. **Using the Web Interface**:
   - **Business Mode**: Send professional notifications with business name
   - **Leisure Mode**: Send personal alerts to contact groups
   - **Contacts**: Manage your contact list and groups

### Desktop Application

1. **Launch the GUI**:
   ```bash
   python src/main.py
   ```

2. **Features**:
   - Visual contact management
   - Location monitoring setup
   - Message template customization

## Configuration

### Predefined Locations
The system comes with default locations that can be customized:
- **California**: Covers major California destinations
- **Washington DC**: Metro area coverage

### Message Templates
The system uses configurable message templates stored in `config/message_templates.json`:
- **Basic Arrival**: Professional arrival notification
- **Formal Arrival**: Formal business notification  
- **Casual Arrival**: Friendly personal notification
- **Custom Messages**: Create your own templates via the web interface

Templates can be customized by editing the JSON configuration file.

### Contact Groups
Organize contacts into groups for bulk notifications:
- Create custom groups via web interface
- Assign contacts to multiple groups
- Send group-specific messages

## File Structure

```
OnArrival/
├── src/
│   ├── gui/                 # PyQt6 desktop interface
│   ├── models/              # Data models (Contact, Location, Group)
│   ├── services/            # Core services (Notification, Location, Storage)
│   ├── static/              # Web assets (CSS, JS, images)
│   ├── templates/           # HTML templates
│   ├── main.py              # Desktop app entry point
│   └── web_app.py           # Flask web application
├── contacts.json            # Contact storage
├── groups.json              # Group storage
├── requirements.txt         # Python dependencies
├── wsgi.py                  # WSGI entry point
└── README.md
```

## API Endpoints

### Web API
- `GET /` - Main web interface
- `POST /api/send_leisure` - Send leisure alerts
- `POST /api/send_business` - Send business alerts
- `GET/POST /api/groups` - Manage contact groups

## Development

### Running in Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with hot reload
python src/web_app.py
```

### Adding New Features
1. Models go in `src/models/`
2. Business logic in `src/services/`
3. Web routes in `src/web_app.py`
4. GUI components in `src/gui/`

## Deployment

### Production Deployment
1. Configure production environment variables
2. Use Gunicorn for WSGI serving:
   ```bash
   gunicorn --bind 0.0.0.0:8000 wsgi:application
   ```

### PythonAnywhere Deployment
The project is configured for PythonAnywhere deployment:
- Update `PYTHONANYWHERE_DOMAIN` in `.env`
- Upload files to PythonAnywhere
- Configure WSGI file path

## Troubleshooting

### Common Issues
1. **Twilio Authentication**: Verify credentials in `.env` file
2. **Import Errors**: Ensure virtual environment is activated
3. **PyQt6 Issues**: Install system Qt6 libraries if needed
4. **Phone Number Format**: Use E.164 format (+1XXXXXXXXXX)

### Logs
- Check console output for Twilio API responses
- Web server logs show request/response details
- Desktop app prints GUI events to terminal

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for personal/educational use. Twilio usage subject to their terms of service.

## Acknowledgments

- Built with Twilio for voice/SMS services
- Uses Flask for web framework
- PyQt6 for desktop GUI
- Bootstrap for responsive web design

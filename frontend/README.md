# OnArrival Frontend

A modern React web application for the OnArrival notification system.

## Features

- 🎨 Modern, responsive UI with Tailwind CSS
- 📱 Mobile-friendly design with PWA support
- 🔐 API key authentication
- 📞 Business alert functionality
- 👥 Leisure alerts for contact groups
- 📋 Contact group management
- ⚙️ Settings configuration
- 🔥 Real-time toast notifications
- 🎯 Form validation with React Hook Form

## Tech Stack

- **React 18** - UI framework
- **React Router 6** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Heroicons** - SVG icon library
- **React Hook Form** - Form handling and validation
- **Axios** - HTTP client for API calls
- **React Hot Toast** - Toast notifications

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- OnArrival backend server running on port 5001

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Update environment variables if needed (defaults should work for development)

5. Start the development server:
   ```bash
   npm start
   ```

The application will open at `http://localhost:3000`

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (⚠️ irreversible)

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Logo.jsx
│   │   └── LoadingSpinner.jsx
│   ├── hooks/            # Custom React hooks
│   │   └── useGroups.js
│   ├── pages/            # Page components
│   │   ├── Dashboard.jsx
│   │   ├── BusinessAlert.jsx
│   │   ├── LeisureAlert.jsx
│   │   ├── Contacts.jsx
│   │   └── Settings.jsx
│   ├── services/         # API service layer
│   │   └── api.js
│   ├── App.js           # Main app component
│   ├── index.js         # App entry point
│   └── index.css        # Global styles
├── tailwind.config.js   # Tailwind configuration
├── postcss.config.js    # PostCSS configuration
└── package.json
```

## API Integration

The frontend communicates with the OnArrival backend through REST API endpoints:

- `POST /api/auth` - Authentication
- `POST /api/send_business` - Send business alerts
- `POST /api/send_leisure` - Send leisure alerts
- `GET /api/groups` - Get contact groups
- `GET /api/scripts` - Get message templates

### API Key Configuration

The application uses API keys for authentication:

1. **Development**: Uses default dev key automatically
2. **Production**: Configure custom API key in Settings page
3. **Environment**: Set `REACT_APP_API_KEY` environment variable

## Features Overview

### Dashboard
- Central navigation hub
- Quick access to all features
- System status overview

### Business Alerts
- Professional notification sending
- Individual contact targeting
- Timer-based scheduling
- Form validation

### Leisure Alerts
- Group-based notifications
- Personalized messaging with contact names
- Contact group selection
- Friendly, casual interface

### Contact Management
- View existing contact groups
- Contact details display
- Integration with backend data
- Future CRUD operations support

### Settings
- API key configuration
- Authentication testing
- System information
- Development tools

## Styling

The application uses Tailwind CSS with a custom design system:

- **Primary**: Blue color scheme
- **Success**: Green for positive actions
- **Warning**: Yellow for cautionary messages
- **Error**: Red for error states
- **Gradients**: Modern gradient backgrounds
- **Animations**: Smooth transitions and micro-interactions

### Custom Components

Predefined CSS classes for consistent styling:
- `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`
- `.card` - Container styling
- `.form-input`, `.form-textarea`, `.form-select` - Form controls

## Mobile Support

- Responsive design for all screen sizes
- Touch-friendly interface
- PWA manifest for mobile installation
- Optimized for iOS and Android

## Development

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.js`
3. Update navigation in Dashboard component

### Adding API Endpoints

1. Add method to appropriate API module in `src/services/api.js`
2. Create custom hook if needed in `src/hooks/`
3. Use in component with proper error handling

### Styling Guidelines

- Use Tailwind utility classes
- Follow existing color scheme
- Maintain consistent spacing and typography
- Test on mobile devices

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `build/` directory ready for deployment.

## Backend Integration

Ensure the OnArrival backend is running on port 5001 (or update `REACT_APP_API_URL`):

```bash
# In the main OnArrival directory
cd src
python web_app.py --port 5001
```

## Contributing

1. Follow existing code style and patterns
2. Add proper TypeScript types where beneficial
3. Test on multiple devices and browsers
4. Update documentation for new features 
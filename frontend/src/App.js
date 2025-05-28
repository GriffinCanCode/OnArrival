import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Pages
import Dashboard from './pages/Dashboard';
import BusinessAlert from './pages/BusinessAlert';
import LeisureAlert from './pages/LeisureAlert';
import Contacts from './pages/Contacts';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/business" element={<BusinessAlert />} />
          <Route path="/leisure" element={<LeisureAlert />} />
          <Route path="/contacts" element={<Contacts />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
        
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              style: {
                background: '#059669',
              },
            },
            error: {
              duration: 5000,
              style: {
                background: '#DC2626',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App; 
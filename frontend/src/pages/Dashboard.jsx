import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BuildingOfficeIcon, 
  UserGroupIcon, 
  HeartIcon,
  Cog6ToothIcon 
} from '@heroicons/react/24/outline';
import Logo from '../components/Logo';

const Dashboard = () => {
  const navigate = useNavigate();

  const menuItems = [
    {
      title: 'Business Alert',
      description: 'Send professional notifications',
      icon: BuildingOfficeIcon,
      path: '/business',
      color: 'from-blue-500 to-blue-600',
    },
    {
      title: 'Leisure Alert',
      description: 'Send personal notifications to groups',
      icon: HeartIcon,
      path: '/leisure',
      color: 'from-green-500 to-green-600',
    },
    {
      title: 'Contacts',
      description: 'Manage contact groups',
      icon: UserGroupIcon,
      path: '/contacts',
      color: 'from-purple-500 to-purple-600',
    },
    {
      title: 'Settings',
      description: 'Configure application',
      icon: Cog6ToothIcon,
      path: '/settings',
      color: 'from-gray-500 to-gray-600',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <Logo size="xl" className="mx-auto mb-6" />
          <h1 className="text-4xl font-bold text-gray-900 mb-2">OnArrival</h1>
          <p className="text-lg text-gray-600">Smart notification system for arrivals and alerts</p>
        </div>

        {/* Menu Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-slide-in">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={item.path}
                className="card cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
                onClick={() => navigate(item.path)}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-r ${item.color}`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">
                      {item.title}
                    </h3>
                    <p className="text-gray-600">{item.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Stats */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card text-center">
            <h4 className="text-2xl font-bold text-primary-600 mb-2">24/7</h4>
            <p className="text-gray-600">Service Availability</p>
          </div>
          <div className="card text-center">
            <h4 className="text-2xl font-bold text-success-600 mb-2">Instant</h4>
            <p className="text-gray-600">Notification Delivery</p>
          </div>
          <div className="card text-center">
            <h4 className="text-2xl font-bold text-purple-600 mb-2">Secure</h4>
            <p className="text-gray-600">Encrypted Communications</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 
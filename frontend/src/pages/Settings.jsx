import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ArrowLeftIcon, Cog6ToothIcon, KeyIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const Settings = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [apiKeyStatus, setApiKeyStatus] = useState(null);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm();

  useEffect(() => {
    // Load current API key from localStorage
    const currentApiKey = localStorage.getItem('apiKey');
    if (currentApiKey) {
      setValue('apiKey', currentApiKey);
      checkApiKeyStatus(currentApiKey);
    }
  }, [setValue]);

  const checkApiKeyStatus = async (apiKey) => {
    try {
      setLoading(true);
      const response = await authAPI.authenticate(apiKey);
      if (response.success) {
        setApiKeyStatus({
          valid: true,
          permissions: response.permissions,
          expiresIn: response.expires_in,
        });
      }
    } catch (error) {
      setApiKeyStatus({
        valid: false,
        error: error.response?.data?.error || 'Invalid API key',
      });
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      const apiKey = data.apiKey.trim();
      
      // Test the API key
      const response = await authAPI.authenticate(apiKey);
      
      if (response.success) {
        // Save to localStorage
        localStorage.setItem('apiKey', apiKey);
        localStorage.setItem('sessionToken', response.session_token);
        
        setApiKeyStatus({
          valid: true,
          permissions: response.permissions,
          expiresIn: response.expires_in,
        });
        
        toast.success('API key saved successfully!');
      } else {
        throw new Error(response.error || 'Invalid API key');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Failed to validate API key';
      setApiKeyStatus({
        valid: false,
        error: errorMessage,
      });
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearApiKey = () => {
    localStorage.removeItem('apiKey');
    localStorage.removeItem('sessionToken');
    setValue('apiKey', '');
    setApiKeyStatus(null);
    toast.success('API key cleared');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="btn-secondary mr-4 p-2"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-gradient-to-r from-gray-500 to-gray-600 mr-4">
              <Cog6ToothIcon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
              <p className="text-gray-600">Configure your application settings</p>
            </div>
          </div>
        </div>

        {/* API Key Configuration */}
        <div className="card">
          <div className="flex items-center mb-6">
            <KeyIcon className="w-6 h-6 text-primary-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">API Key Configuration</h2>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
                OnArrival API Key
              </label>
              <input
                type="password"
                id="apiKey"
                className="form-input"
                placeholder="Enter your API key"
                {...register('apiKey', {
                  required: 'API key is required',
                  minLength: {
                    value: 10,
                    message: 'API key must be at least 10 characters',
                  },
                })}
              />
              {errors.apiKey && (
                <p className="mt-1 text-sm text-error-600">{errors.apiKey.message}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                Enter your OnArrival API key to authenticate with the service
              </p>
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex items-center"
              >
                {loading ? (
                  <LoadingSpinner size="sm" text="" />
                ) : (
                  <>
                    <ShieldCheckIcon className="w-4 h-4 mr-2" />
                    Validate & Save
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={clearApiKey}
                className="btn-secondary"
                disabled={loading}
              >
                Clear
              </button>
            </div>
          </form>

          {/* API Key Status */}
          {apiKeyStatus && (
            <div className={`mt-6 p-4 rounded-lg ${
              apiKeyStatus.valid 
                ? 'bg-success-50 border border-success-200' 
                : 'bg-error-50 border border-error-200'
            }`}>
              <div className="flex items-center mb-2">
                <ShieldCheckIcon className={`w-5 h-5 mr-2 ${
                  apiKeyStatus.valid ? 'text-success-600' : 'text-error-600'
                }`} />
                <h3 className={`font-semibold ${
                  apiKeyStatus.valid ? 'text-success-900' : 'text-error-900'
                }`}>
                  {apiKeyStatus.valid ? 'API Key Valid' : 'API Key Invalid'}
                </h3>
              </div>
              
              {apiKeyStatus.valid ? (
                <div className="space-y-2 text-sm text-success-800">
                  <p><strong>Permissions:</strong> {apiKeyStatus.permissions?.join(', ') || 'None'}</p>
                  <p><strong>Session expires in:</strong> {apiKeyStatus.expiresIn} seconds</p>
                </div>
              ) : (
                <p className="text-sm text-error-800">{apiKeyStatus.error}</p>
              )}
            </div>
          )}
        </div>

        {/* Development Info */}
        <div className="mt-8 card bg-blue-50 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">🔧 Development Information</h3>
          <div className="text-sm text-blue-800 space-y-2">
            <p><strong>Default Development API Key:</strong></p>
            <code className="block bg-blue-100 p-2 rounded text-xs">
              dev-key-bf2790480a957082962da276a43f652e
            </code>
            <p className="text-xs text-blue-600">
              This key is automatically used if no custom key is provided
            </p>
          </div>
        </div>

        {/* API Information */}
        <div className="mt-6 card bg-gray-50 border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📡 API Endpoints</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="font-medium">Authentication:</span>
              <code className="text-xs bg-gray-200 px-2 py-1 rounded">POST /api/auth</code>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Business Alerts:</span>
              <code className="text-xs bg-gray-200 px-2 py-1 rounded">POST /api/send_business</code>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Leisure Alerts:</span>
              <code className="text-xs bg-gray-200 px-2 py-1 rounded">POST /api/send_leisure</code>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Contact Groups:</span>
              <code className="text-xs bg-gray-200 px-2 py-1 rounded">GET /api/groups</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ArrowLeftIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';
import { alertAPI } from '../services/api';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const BusinessAlert = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    reset,
  } = useForm({
    defaultValues: {
      use_timer: false,
      timer_minutes: 30,
    },
  });

  const useTimer = watch('use_timer');

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      const alertData = {
        business_name: data.business_name.trim(),
        phone: data.phone.trim(),
        message: data.message.trim(),
        ...(data.use_timer && { timer_minutes: parseInt(data.timer_minutes) }),
      };

      const response = await alertAPI.sendBusinessAlert(alertData);
      
      if (response.success) {
        toast.success(`Alert sent successfully! ${response.message || ''}`);
        reset();
      } else {
        throw new Error(response.error || 'Failed to send alert');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Failed to send alert';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-50 py-8 px-4">
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
            <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 mr-4">
              <BuildingOfficeIcon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Business Alert</h1>
              <p className="text-gray-600">Send professional arrival notifications</p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="card">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Business Name */}
            <div>
              <label htmlFor="business_name" className="block text-sm font-medium text-gray-700 mb-2">
                Business Name *
              </label>
              <input
                type="text"
                id="business_name"
                className="form-input"
                placeholder="Enter business name"
                {...register('business_name', {
                  required: 'Business name is required',
                  minLength: {
                    value: 2,
                    message: 'Business name must be at least 2 characters',
                  },
                  maxLength: {
                    value: 100,
                    message: 'Business name must be less than 100 characters',
                  },
                })}
              />
              {errors.business_name && (
                <p className="mt-1 text-sm text-error-600">{errors.business_name.message}</p>
              )}
            </div>

            {/* Phone Number */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number *
              </label>
              <input
                type="tel"
                id="phone"
                className="form-input"
                placeholder="+1 (555) 123-4567"
                {...register('phone', {
                  required: 'Phone number is required',
                  pattern: {
                    value: /^[\+]?[\d\s\(\)\-\.]{10,}$/,
                    message: 'Please enter a valid phone number',
                  },
                })}
              />
              {errors.phone && (
                <p className="mt-1 text-sm text-error-600">{errors.phone.message}</p>
              )}
            </div>

            {/* Message */}
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                Message *
              </label>
              <textarea
                id="message"
                rows={4}
                className="form-textarea"
                placeholder="Enter your message..."
                {...register('message', {
                  required: 'Message is required',
                  minLength: {
                    value: 10,
                    message: 'Message must be at least 10 characters',
                  },
                  maxLength: {
                    value: 500,
                    message: 'Message must be less than 500 characters',
                  },
                })}
              />
              {errors.message && (
                <p className="mt-1 text-sm text-error-600">{errors.message.message}</p>
              )}
            </div>

            {/* Timer Option */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="use_timer"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                {...register('use_timer')}
              />
              <label htmlFor="use_timer" className="ml-2 block text-sm text-gray-700">
                Use timer for delayed notification
              </label>
            </div>

            {useTimer && (
              <div>
                <label htmlFor="timer_minutes" className="block text-sm font-medium text-gray-700 mb-2">
                  Timer (minutes)
                </label>
                <input
                  type="number"
                  id="timer_minutes"
                  min="1"
                  max="120"
                  className="form-input"
                  {...register('timer_minutes', {
                    min: {
                      value: 1,
                      message: 'Timer must be at least 1 minute',
                    },
                    max: {
                      value: 120,
                      message: 'Timer cannot exceed 120 minutes',
                    },
                  })}
                />
                {errors.timer_minutes && (
                  <p className="mt-1 text-sm text-error-600">{errors.timer_minutes.message}</p>
                )}
              </div>
            )}

            {/* Submit Button */}
            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex-1 flex items-center justify-center"
              >
                {loading ? (
                  <LoadingSpinner size="sm" text="" />
                ) : (
                  'Send Business Alert'
                )}
              </button>
              <button
                type="button"
                onClick={() => reset()}
                className="btn-secondary"
                disabled={loading}
              >
                Clear
              </button>
            </div>
          </form>
        </div>

        {/* Info Card */}
        <div className="mt-8 card bg-blue-50 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 Business Alert Tips</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Include your business name for professional identification</li>
            <li>• Use clear, concise messages for better delivery</li>
            <li>• Timer option allows for scheduled notifications</li>
            <li>• Test with your own number first to verify functionality</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default BusinessAlert; 
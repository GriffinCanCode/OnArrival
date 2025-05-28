import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ArrowLeftIcon, HeartIcon, UsersIcon } from '@heroicons/react/24/outline';
import { alertAPI } from '../services/api';
import { useGroups } from '../hooks/useGroups';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const LeisureAlert = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const { groups, loading: groupsLoading, error: groupsError } = useGroups();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      const alertData = {
        group: data.group,
        message: data.message.trim(),
      };

      const response = await alertAPI.sendLeisureAlert(alertData);
      
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
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-gray-50 py-8 px-4">
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
            <div className="p-3 rounded-lg bg-gradient-to-r from-green-500 to-green-600 mr-4">
              <HeartIcon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Leisure Alert</h1>
              <p className="text-gray-600">Send personal notifications to contact groups</p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="card">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Group Selection */}
            <div>
              <label htmlFor="group" className="block text-sm font-medium text-gray-700 mb-2">
                Contact Group *
              </label>
              {groupsLoading ? (
                <div className="flex items-center justify-center py-4">
                  <LoadingSpinner size="sm" text="Loading groups..." />
                </div>
              ) : groupsError ? (
                <div className="bg-error-50 border border-error-200 rounded-lg p-4">
                  <p className="text-error-600 text-sm">
                    Error loading groups: {groupsError}
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate('/contacts')}
                    className="mt-2 text-error-700 underline text-sm"
                  >
                    Manage contact groups
                  </button>
                </div>
              ) : (
                <select
                  id="group"
                  className="form-select"
                  {...register('group', {
                    required: 'Please select a contact group',
                  })}
                >
                  <option value="">Select a group</option>
                  {groups.map((group) => (
                    <option key={group.name} value={group.name}>
                      {group.name} ({group.contacts?.length || 0} contacts)
                    </option>
                  ))}
                </select>
              )}
              {errors.group && (
                <p className="mt-1 text-sm text-error-600">{errors.group.message}</p>
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
                placeholder="Enter your message... Use () as a placeholder for contact names"
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
              <p className="mt-1 text-sm text-gray-500">
                Tip: Use () in your message to automatically insert each contact's name
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={loading || groupsLoading}
                className="btn-success flex-1 flex items-center justify-center"
              >
                {loading ? (
                  <LoadingSpinner size="sm" text="" />
                ) : (
                  'Send Leisure Alert'
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

        {/* Groups Overview */}
        {!groupsLoading && !groupsError && groups.length > 0 && (
          <div className="mt-8 card bg-green-50 border-green-200">
            <div className="flex items-center mb-4">
              <UsersIcon className="w-5 h-5 text-green-600 mr-2" />
              <h3 className="text-lg font-semibold text-green-900">Available Groups</h3>
            </div>
            <div className="space-y-2">
              {groups.map((group) => (
                <div
                  key={group.name}
                  className="flex justify-between items-center py-2 px-3 bg-white rounded border"
                >
                  <span className="font-medium text-gray-900">{group.name}</span>
                  <span className="text-sm text-gray-600">
                    {group.contacts?.length || 0} contacts
                  </span>
                </div>
              ))}
            </div>
            <button
              onClick={() => navigate('/contacts')}
              className="mt-4 text-green-700 underline text-sm"
            >
              Manage contact groups
            </button>
          </div>
        )}

        {/* No Groups Message */}
        {!groupsLoading && !groupsError && groups.length === 0 && (
          <div className="mt-8 card bg-warning-50 border-warning-200">
            <h3 className="text-lg font-semibold text-warning-900 mb-2">No Contact Groups</h3>
            <p className="text-warning-800 mb-4">
              You haven't created any contact groups yet. Create groups to send leisure alerts.
            </p>
            <button
              onClick={() => navigate('/contacts')}
              className="btn-primary"
            >
              Create Contact Groups
            </button>
          </div>
        )}

        {/* Info Card */}
        <div className="mt-8 card bg-green-50 border-green-200">
          <h3 className="text-lg font-semibold text-green-900 mb-2">💡 Leisure Alert Tips</h3>
          <ul className="text-sm text-green-800 space-y-1">
            <li>• Use () in your message to personalize with contact names</li>
            <li>• Perfect for notifying friends and family of arrivals</li>
            <li>• Messages are sent to all contacts in the selected group</li>
            <li>• Keep messages friendly and conversational</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LeisureAlert; 
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, UserGroupIcon, PlusIcon } from '@heroicons/react/24/outline';
import { useGroups } from '../hooks/useGroups';
import LoadingSpinner from '../components/LoadingSpinner';

const Contacts = () => {
  const navigate = useNavigate();
  const { groups, loading, error, refetch } = useGroups();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="btn-secondary mr-4 p-2"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-gradient-to-r from-purple-500 to-purple-600 mr-4">
              <UserGroupIcon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Contact Groups</h1>
              <p className="text-gray-600">Manage your contact groups for notifications</p>
            </div>
          </div>
        </div>

        {/* Add Group Button */}
        <div className="mb-6">
          <button
            onClick={() => {/* TODO: Add group functionality */}}
            className="btn-primary flex items-center"
          >
            <PlusIcon className="w-5 h-5 mr-2" />
            Add New Group
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="card">
            <LoadingSpinner text="Loading contact groups..." />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="card bg-error-50 border-error-200">
            <h3 className="text-lg font-semibold text-error-900 mb-2">Error Loading Groups</h3>
            <p className="text-error-800 mb-4">{error}</p>
            <button onClick={refetch} className="btn-primary">
              Try Again
            </button>
          </div>
        )}

        {/* Groups List */}
        {!loading && !error && (
          <>
            {groups.length === 0 ? (
              <div className="card text-center">
                <UserGroupIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Contact Groups</h3>
                <p className="text-gray-600 mb-6">
                  Create your first contact group to start sending notifications.
                </p>
                <button
                  onClick={() => {/* TODO: Add group functionality */}}
                  className="btn-primary"
                >
                  Create Your First Group
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {groups.map((group, index) => (
                  <div
                    key={group.name}
                    className="card animate-slide-in"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-1">
                          {group.name}
                        </h3>
                        <p className="text-gray-600">
                          {group.contacts?.length || 0} contacts
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <button className="btn-secondary text-sm">
                          Edit
                        </button>
                        <button className="btn-danger text-sm">
                          Delete
                        </button>
                      </div>
                    </div>

                    {/* Contacts List */}
                    {group.contacts && group.contacts.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="font-medium text-gray-700 mb-2">Contacts:</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {group.contacts.map((contact, contactIndex) => (
                            <div
                              key={contactIndex}
                              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                            >
                              <div>
                                <p className="font-medium text-gray-900">{contact.name}</p>
                                <p className="text-sm text-gray-600">{contact.phone}</p>
                              </div>
                              <button className="text-error-600 hover:text-error-700 text-sm">
                                Remove
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Add Contact Button */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <button className="btn-secondary text-sm flex items-center">
                        <PlusIcon className="w-4 h-4 mr-1" />
                        Add Contact
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Info Card */}
        <div className="mt-8 card bg-purple-50 border-purple-200">
          <h3 className="text-lg font-semibold text-purple-900 mb-2">💡 Contact Management Tips</h3>
          <ul className="text-sm text-purple-800 space-y-1">
            <li>• Create groups to organize contacts by relationship or purpose</li>
            <li>• Use descriptive group names like "Family", "Work Team", or "Friends"</li>
            <li>• Each group can have unlimited contacts</li>
            <li>• Groups are used for sending leisure alerts to multiple people</li>
          </ul>
        </div>

        {/* Note about management */}
        <div className="mt-6 card bg-warning-50 border-warning-200">
          <h4 className="font-semibold text-warning-900 mb-2">📝 Note</h4>
          <p className="text-sm text-warning-800">
            Contact management functionality is integrated with the backend system. 
            Currently displaying read-only data from the API. Full CRUD operations 
            would require additional backend endpoints for contact management.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Contacts; 
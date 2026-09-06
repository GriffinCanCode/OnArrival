import { useState, useEffect } from 'react';
import { groupAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useGroups = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await groupAPI.getGroups();
      
      if (response.success) {
        setGroups(response.groups || []);
      } else {
        throw new Error(response.error || 'Failed to fetch groups');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to fetch groups';
      setError(errorMessage);
      toast.error(errorMessage);
      setGroups([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  return {
    groups,
    loading,
    error,
    refetch: fetchGroups,
  };
}; 
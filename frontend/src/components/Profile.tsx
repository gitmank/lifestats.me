'use client';

import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Plus, Trash2, Copy, Check, AlertTriangle, User, Key, Calendar, Download, LogOut, X } from 'lucide-react';
import { APIKeyInfo, NewAPIKey, UserInfo, apiClient } from '@/lib/api';

interface ProfileProps {
  username: string;
  onBack: () => void;
  onLogout: () => void;
}

// SHA-256 hash function for client-side verification
async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}

export default function Profile({ username, onBack, onLogout }: ProfileProps) {
  const [apiKeys, setApiKeys] = useState<APIKeyInfo[]>([]);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [creatingKey, setCreatingKey] = useState(false);
  const [newKeyData, setNewKeyData] = useState<NewAPIKey | null>(null);
  const [copiedKey, setCopiedKey] = useState('');
  const [deletingKeyId, setDeletingKeyId] = useState<number | null>(null);
  const [showDeleteAccount, setShowDeleteAccount] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [deletingAccount, setDeletingAccount] = useState(false);
  const [currentKeyHash, setCurrentKeyHash] = useState<string>('');
  
  // SHA hash info popup state
  const [showHashInfo, setShowHashInfo] = useState(false);
  const [testKey, setTestKey] = useState('');
  const [computedHash, setComputedHash] = useState('');

  const fetchUserInfo = async () => {
    try {
      const user = await apiClient.getCurrentUser();
      setUserInfo(user);
    } catch (err) {
      console.error('Failed to fetch user info:', err);
      setError('Failed to load user information');
    }
  };

  const fetchAPIKeys = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const keys = await apiClient.listAPIKeys(username);
      setApiKeys(keys);
    } catch (err) {
      console.error('Failed to fetch API keys:', err);
      setError('Failed to load API keys');
    } finally {
      setLoading(false);
    }
  }, [username]);

  const calculateMemberSinceDays = () => {
    if (!userInfo?.created_at) return 'Unknown';
    const createdDate = new Date(userInfo.created_at);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - createdDate.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays.toString();
  };

  const handleCreateAPIKey = async () => {
    try {
      setCreatingKey(true);
      setError('');
      const newKey = await apiClient.createAPIKey(username);
      setNewKeyData(newKey);
      await fetchAPIKeys(); // Refresh the list
    } catch (err) {
      console.error('Failed to create API key:', err);
      setError('Failed to create API key');
    } finally {
      setCreatingKey(false);
    }
  };

  const handleDeleteAPIKey = async (keyId: number) => {
    try {
      setDeletingKeyId(keyId);
      setError('');
      
      await apiClient.deleteAPIKeyById(username, keyId);
      await fetchAPIKeys(); // Refresh the list
    } catch (err) {
      console.error('Failed to delete API key:', err);
      setError('Failed to delete API key');
    } finally {
      setDeletingKeyId(null);
    }
  };

  const handleCopyKey = async (token: string) => {
    try {
      await navigator.clipboard.writeText(token);
      setCopiedKey(token);
      setTimeout(() => setCopiedKey(''), 2000);
    } catch (err) {
      console.error('Failed to copy API key:', err);
    }
  };

  const handleDownloadKey = (token: string) => {
    const content = `Life Stats API Key
==================

Username: ${username}
API Key: ${token}

Keep this API key safe! You can use it to access your Life Stats dashboard.

Instructions:
1. Copy the API key above
2. Use it in the "Sign In" tab to access your dashboard
3. You can generate additional API keys from your profile if needed

Generated on: ${new Date().toLocaleString()}
`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lifestats-api-key-${username}-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== username) {
      setError('Username confirmation does not match');
      return;
    }

    try {
      setDeletingAccount(true);
      setError('');
      await apiClient.deleteAccount(username);
      
      // Clear local storage and logout
      localStorage.removeItem('authToken');
      localStorage.removeItem('username');
      onLogout();
    } catch (err) {
      console.error('Failed to delete account:', err);
      setError('Failed to delete account');
      setDeletingAccount(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Update computed hash when test key changes
  useEffect(() => {
    if (testKey) {
      sha256(testKey).then(hash => {
        setComputedHash(hash);
      });
    } else {
      setComputedHash('');
    }
  }, [testKey]);

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([
        fetchUserInfo(),
        fetchAPIKeys()
      ]);
    };
    
    const calculateCurrentKeyHash = async () => {
      const authToken = localStorage.getItem('authToken');
      if (authToken) {
        const hash = await sha256(authToken);
        setCurrentKeyHash(hash.slice(-8));
      }
    };
    
    fetchData();
    calculateCurrentKeyHash();
  }, [fetchAPIKeys]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-green-100">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-800">Profile Settings</h1>
                  <p className="text-sm text-gray-600">Manage your account and API keys</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        {/* User Info */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Account Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900 font-medium">
                {username}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Member Since</label>
              <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-600">
                {calculateMemberSinceDays()} days
              </div>
            </div>
          </div>
          <div className="flex justify-end">
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 bg-red-100 hover:bg-red-200 text-red-700 px-4 py-2 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        {/* API Keys Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-800">API Keys</h2>
              <p className="text-sm text-gray-600 mt-1">
                Manage your API keys for accessing the Life Stats API ({apiKeys.length}/5)
              </p>
            </div>
            <button
              onClick={handleCreateAPIKey}
              disabled={creatingKey || apiKeys.length >= 5}
              className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors"
              title={apiKeys.length >= 5 ? "API key limit reached (5/5)" : "Create new API key"}
            >
              <Plus className="w-4 h-4" />
              <span>{creatingKey ? 'Creating...' : 'New API Key'}</span>
            </button>
          </div>

          {apiKeys.length >= 5 && (
            <div className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg text-sm mb-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4" />
                <span>
                  You&apos;ve reached the maximum of 5 API keys. Delete an existing key to create a new one.
                </span>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">
              {error}
            </div>
          )}

          {/* New Key Display */}
          {newKeyData && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-green-800">New API Key Created</h3>
                  <p className="text-sm text-green-600 mt-1">Copy this key now - it won&apos;t be shown again</p>
                </div>
                <button
                  onClick={() => setNewKeyData(null)}
                  className="text-green-600 hover:text-green-800"
                >
                  ×
                </button>
              </div>
              <div className="mt-3 flex items-center space-x-2">
                <div className="flex-1 bg-white border border-green-200 rounded px-3 py-2 font-mono text-sm text-gray-900">
                  {newKeyData.token}
                </div>
                <button
                  onClick={() => handleCopyKey(newKeyData.token)}
                  className="p-2 hover:bg-green-100 rounded transition-colors"
                  title="Copy API key"
                >
                  {copiedKey === newKeyData.token ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4 text-green-600" />
                  )}
                </button>
                <button
                  onClick={() => handleDownloadKey(newKeyData.token)}
                  className="p-2 hover:bg-green-100 rounded transition-colors"
                  title="Download API key"
                >
                  <Download className="w-4 h-4 text-green-600" />
                </button>
              </div>
            </div>
          )}

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading API keys...</p>
            </div>
          ) : apiKeys.length === 0 ? (
            <div className="text-center py-8">
              <Key className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">No API keys found</p>
              <p className="text-sm text-gray-500">Create your first API key to get started</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-700">
                      <div className="flex items-center space-x-2">
                        <span>Key Hash:</span>
                        <button
                          onClick={() => setShowHashInfo(true)}
                          className="p-1 hover:bg-yellow-100 rounded-full transition-colors"
                          title="Learn about SHA-256 previews"
                        >
                          <AlertTriangle className="w-4 h-4 text-yellow-500" />
                        </button>
                      </div>
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Created</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {apiKeys.map((key) => (
                    <tr key={key.id} className={`border-b border-gray-100 hover:bg-gray-50 ${
                      key.key_preview === currentKeyHash 
                        ? 'bg-blue-50 border-blue-200 hover:bg-blue-100' 
                        : ''
                    }`}>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono text-gray-800">
                            ****{key.key_preview}
                          </code>
                          {key.key_preview === currentKeyHash && (
                            <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">
                              Current
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-4 h-4" />
                          <span>{formatDate(key.created_at)}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => handleDeleteAPIKey(key.id)}
                          disabled={deletingKeyId === key.id}
                          className="p-2 hover:bg-red-100 rounded-full transition-colors group"
                          title="Delete API key"
                        >
                          <Trash2 className="w-4 h-4 text-gray-400 group-hover:text-red-600" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <h2 className="text-lg font-semibold text-red-600">Danger Zone</h2>
          </div>
          <p className="text-gray-600 mb-6">
            Once you delete your account, there is no going back. This will permanently delete your profile, 
            all your metrics data, goals, and API keys.
          </p>
          
          {!showDeleteAccount ? (
            <button
              onClick={() => setShowDeleteAccount(true)}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Delete Account
            </button>
          ) : (
            <div className="border border-red-200 rounded-lg p-4 bg-red-50">
              <p className="text-red-800 font-medium mb-3">
                Are you sure you want to delete your account?
              </p>
              <p className="text-sm text-red-600 mb-4">
                Type your username <strong>{username}</strong> to confirm:
              </p>
              <div className="space-y-4">
                <input
                  type="text"
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full px-3 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900"
                />
                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      setShowDeleteAccount(false);
                      setDeleteConfirmText('');
                      setError('');
                    }}
                    disabled={deletingAccount}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDeleteAccount}
                    disabled={deletingAccount || deleteConfirmText !== username}
                    className="px-4 py-2 bg-red-500 hover:bg-red-600 disabled:bg-red-300 text-white rounded-lg transition-colors"
                  >
                    {deletingAccount ? 'Deleting...' : 'Delete Account'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* SHA Hash Info Popup */}
      {showHashInfo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">About Key Previews</h3>
              <button
                onClick={() => setShowHashInfo(false)}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="space-y-4 text-sm text-gray-600">
              <p>
                For security reasons, we don&apos;t store your actual API keys. Instead, we store and display 
                the <strong>last 8 characters of the SHA-256 hash</strong> of your key as a preview.
              </p>
              
              <p>
                This allows you to identify your keys without exposing the actual token values. 
                You can verify which key is which by pasting your key below:
              </p>
              
              <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Paste API Key to Verify:
                </label>
                <input
                  type="text"
                  value={testKey}
                  onChange={(e) => setTestKey(e.target.value)}
                  placeholder="e.g., 21d0aa98-ebcc-4154-98a2-d5e8fc4f49f6"
                  className="w-full px-3 py-2 border border-gray-300 rounded text-gray-900 text-sm font-mono"
                />
                
                {computedHash && (
                  <div className="mt-3">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Key Preview (last 8 chars of SHA-256):
                    </label>
                    <div className="bg-white border border-gray-200 rounded px-3 py-2 text-sm font-mono text-gray-800">
                      ****{computedHash.slice(-8)}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      This should match the preview shown in the table above
                    </p>
                  </div>
                )}
              </div>
              
              <p className="text-xs text-gray-500">
                <strong>Note:</strong> This calculation happens entirely in your browser and is never sent to our servers.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 
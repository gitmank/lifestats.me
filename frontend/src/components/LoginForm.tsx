'use client';

import { useState } from 'react';
import { User, Key } from 'lucide-react';
import { apiClient } from '../lib/api';

interface LoginFormProps {
  onLogin: (username: string, token: string, isNewSignup?: boolean) => void;
}

type AuthTab = 'signin' | 'signup';

export default function LoginForm({ onLogin }: LoginFormProps) {
  const [activeTab, setActiveTab] = useState<AuthTab>('signin');
  const [username, setUsername] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      console.log('Attempting sign in with API key:', apiKey.trim());
      
      // Set the token in localStorage temporarily for the API call
      localStorage.setItem('authToken', apiKey.trim());
      
      // Validate the API key by getting user info
      const userData = await apiClient.getCurrentUser();
      console.log('Sign in success response data:', userData);
      
      // Use the username from the API response
      onLogin(userData.username, apiKey.trim(), false);
    } catch (err) {
      console.error('Sign in error:', err);
      // Remove the invalid token
      localStorage.removeItem('authToken');
      setError('Invalid API key');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      console.log('Attempting signup with username:', username.trim());
      console.log('Request payload:', JSON.stringify({ username: username.trim() }));
      
      const data = await apiClient.signup(username.trim());
      console.log('Success response data:', data);
      onLogin(data.username, data.token, true);
    } catch (err) {
      console.error('Signup error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-3 sm:p-4">
      <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8 w-full max-w-md">
        <div className="text-center mb-6 sm:mb-8">
          <div className="w-12 h-12 sm:w-16 sm:h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
            <User className="w-6 h-6 sm:w-8 sm:h-8 text-green-600" />
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800">Life Stats</h1>
          <p className="text-gray-600 mt-2 text-sm sm:text-base">Track your daily metrics and goals</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex mb-4 sm:mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => {
              setActiveTab('signin');
              setError('');
            }}
            className={`flex-1 py-2 px-3 sm:px-4 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 flex items-center justify-center space-x-1 sm:space-x-2 ${
              activeTab === 'signin'
                ? 'bg-white text-green-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Key className="w-3 h-3 sm:w-4 sm:h-4" />
            <span>Sign In</span>
          </button>
          <button
            onClick={() => {
              setActiveTab('signup');
              setError('');
            }}
            className={`flex-1 py-2 px-3 sm:px-4 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 flex items-center justify-center space-x-1 sm:space-x-2 ${
              activeTab === 'signup'
                ? 'bg-white text-green-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <User className="w-3 h-3 sm:w-4 sm:h-4" />
            <span>Sign Up</span>
          </button>
        </div>

        {/* Sign In Tab */}
        {activeTab === 'signin' && (
          <form onSubmit={handleSignIn} className="space-y-4 sm:space-y-6">
            <div>
              <label htmlFor="apikey" className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="text"
                id="apikey"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all text-gray-900 placeholder-gray-400 bg-white text-sm sm:text-base"
                placeholder="Enter your API key"
                disabled={isLoading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-3 rounded-lg text-xs sm:text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={!apiKey.trim() || isLoading}
              className="w-full bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-medium py-2 sm:py-3 px-4 rounded-lg transition-colors text-sm sm:text-base"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>

            <p className="text-xs text-gray-500 text-center">
              Use your existing API key to access your dashboard
            </p>
          </form>
        )}

        {/* Sign Up Tab */}
        {activeTab === 'signup' && (
          <form onSubmit={handleSignUp} className="space-y-4 sm:space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all text-gray-900 placeholder-gray-400 bg-white text-sm sm:text-base"
                placeholder="Choose a username"
                disabled={isLoading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-3 rounded-lg text-xs sm:text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={!username.trim() || isLoading}
              className="w-full bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-medium py-2 sm:py-3 px-4 rounded-lg transition-colors text-sm sm:text-base"
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>

            <p className="text-xs text-gray-500 text-center">
              No password required - you&apos;ll get an API key after signup
            </p>
          </form>
        )}
      </div>
    </div>
  );
} 
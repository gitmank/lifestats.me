'use client';

import { useState, useEffect } from 'react';
import LoginForm from '@/components/LoginForm';
import Dashboard from '@/components/Dashboard';
import SignupSuccess from '@/components/SignupSuccess';

type AppState = 'loading' | 'login' | 'signup-success' | 'dashboard';

export default function Home() {
  const [appState, setAppState] = useState<AppState>('loading');
  const [user, setUser] = useState<{ username: string; token: string } | null>(null);
  const [signupData, setSignupData] = useState<{ username: string; token: string } | null>(null);

  useEffect(() => {
    // Check for existing auth on page load
    const savedUsername = localStorage.getItem('username');
    const savedToken = localStorage.getItem('authToken');
    
    if (savedUsername && savedToken) {
      setUser({ username: savedUsername, token: savedToken });
      setAppState('dashboard');
    } else {
      setAppState('login');
    }
  }, []);

  const handleLogin = (username: string, token: string, isNewSignup: boolean = false) => {
    const userData = { username, token };
    
    if (isNewSignup) {
      // Show signup success page first
      setSignupData(userData);
      setAppState('signup-success');
    } else {
      // Direct login - go straight to dashboard
      localStorage.setItem('username', username);
      localStorage.setItem('authToken', token);
      setUser(userData);
      setAppState('dashboard');
    }
  };

  const handleSignupContinue = () => {
    if (signupData) {
      localStorage.setItem('username', signupData.username);
      localStorage.setItem('authToken', signupData.token);
      setUser(signupData);
      setSignupData(null);
      setAppState('dashboard');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('username');
    localStorage.removeItem('authToken');
    setUser(null);
    setSignupData(null);
    setAppState('login');
  };

  if (appState === 'loading') {
  return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-3 sm:p-4">
        <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
          <p className="text-gray-600 mt-4 text-sm sm:text-base">Loading...</p>
        </div>
    </div>
  );
  }

  if (appState === 'login') {
    return <LoginForm onLogin={handleLogin} />;
  }

  if (appState === 'signup-success' && signupData) {
    return (
      <SignupSuccess
        username={signupData.username}
        token={signupData.token}
        onContinue={handleSignupContinue}
      />
    );
  }

  if (appState === 'dashboard' && user) {
    return <Dashboard username={user.username} onLogout={handleLogout} />;
  }

  // Fallback
  return <LoginForm onLogin={handleLogin} />;
}

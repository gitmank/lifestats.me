'use client';

import { useState } from 'react';
import { Copy, Download, Check, ArrowRight } from 'lucide-react';

interface SignupSuccessProps {
  username: string;
  token: string;
  onContinue: () => void;
}

export default function SignupSuccess({ username, token, onContinue }: SignupSuccessProps) {
  const [copied, setCopied] = useState(false);

  const copyApiKey = async () => {
    try {
      await navigator.clipboard.writeText(token);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy API key:', err);
    }
  };

  const downloadApiKey = () => {
    const content = `Life Stats API Key
==================

Username: ${username}
API Key: ${token}

Keep this API key safe! You'll need it to sign in to your dashboard.

Instructions:
1. Copy the API key above
2. Use it in the "Sign In" tab to access your dashboard
3. You can generate additional API keys from your dashboard if needed

Generated on: ${new Date().toLocaleString()}
`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lifestats-api-key-${username}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Account Created!</h1>
          <p className="text-gray-600 mt-2">Welcome to Life Stats, {username}</p>
        </div>

        <div className="space-y-6">
          {/* Username Display */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <div className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900">
              {username}
            </div>
          </div>

          {/* API Key Display */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your API Key
            </label>
            <div className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-mono text-sm break-all">
              {token}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Keep this API key safe! You'll need it to sign in to your dashboard.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <div className="flex space-x-3">
              <button
                onClick={copyApiKey}
                className="flex-1 flex items-center justify-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 px-4 rounded-lg transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 text-green-500" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    <span>Copy API Key</span>
                  </>
                )}
              </button>
              
              <button
                onClick={downloadApiKey}
                className="flex-1 flex items-center justify-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 px-4 rounded-lg transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </button>
            </div>

            <button
              onClick={onContinue}
              className="w-full flex items-center justify-center space-x-2 bg-green-500 hover:bg-green-600 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              <span>Continue to Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Important Notice */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h3 className="text-sm font-medium text-yellow-800">Important</h3>
                <p className="text-xs text-yellow-700 mt-1">
                  Make sure to save your API key! You can copy it now or download it as a text file. 
                  You'll use this key to sign in to your dashboard in the future.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 
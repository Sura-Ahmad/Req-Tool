'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login, register, forgotPassword } from '@/lib/api';

type View = 'login' | 'register' | 'forgot';

export default function AuthPage() {
  const router = useRouter();
  const [view, setView] = useState<View>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const reset = (next: View) => {
    setError('');
    setSuccess('');
    setEmail('');
    setPassword('');
    setFullName('');
    setView(next);
  };

  const handleLogin = async () => {
    if (!email || !password) { setError('Please fill in all fields'); return; }
    setLoading(true); setError('');
    try {
      const res = await login(email, password);
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      router.push('/dashboard');
    } catch {
      setError('Invalid email or password');
    } finally { setLoading(false); }
  };

  const handleRegister = async () => {
    if (!fullName || !email || !password) { setError('Please fill in all fields'); return; }
    if (password.length < 8) { setError('Password must be at least 8 characters'); return; }
    setLoading(true); setError('');
    try {
      const res = await register(fullName, email, password);
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      router.push('/dashboard');
    } catch {
      setError('Email already registered');
    } finally { setLoading(false); }
  };

  const handleForgotPassword = async () => {
    if (!email) { setError('Please enter your email address'); return; }
    setLoading(true); setError(''); setSuccess('');
    try {
      await forgotPassword(email);
      setSuccess('If this email is registered, you will receive a password reset link shortly.');
      setEmail('');
    } catch {
      setError('Something went wrong. Please try again.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <h1 className="text-4xl font-bold mb-2" style={{ color: '#1E2A4A' }}>
        Requirements Super Tool
      </h1>
      <p className="text-gray-500 mb-8">Your intelligent requirements management platform</p>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 w-full max-w-md overflow-hidden">

        {/* Tabs — hidden on forgot-password view */}
        {view !== 'forgot' && (
          <div className="flex">
            <button
              onClick={() => reset('login')}
              className="flex-1 py-4 font-semibold text-sm transition-all"
              style={{
                background: view === 'login' ? '#1E2A4A' : '#F3F4F6',
                color: view === 'login' ? 'white' : '#374151',
                borderRadius: view === 'login' ? '16px 16px 0 0' : '0',
              }}
            >Login</button>
            <button
              onClick={() => reset('register')}
              className="flex-1 py-4 font-semibold text-sm transition-all"
              style={{
                background: view === 'register' ? '#1E2A4A' : '#F3F4F6',
                color: view === 'register' ? 'white' : '#374151',
                borderRadius: view === 'register' ? '16px 16px 0 0' : '0',
              }}
            >Register</button>
          </div>
        )}

        {/* Forgot password header */}
        {view === 'forgot' && (
          <div style={{ background: '#1E2A4A' }} className="px-8 py-5 flex items-center gap-3">
            <button
              onClick={() => reset('login')}
              className="text-white opacity-70 hover:opacity-100 transition-opacity text-lg leading-none"
            >&#8592;</button>
            <span className="text-white font-semibold text-sm">Forgot Password</span>
          </div>
        )}

        <div className="p-8">
          {error && (
            <div className="bg-red-50 text-red-500 text-sm px-4 py-3 rounded-xl mb-4">{error}</div>
          )}
          {success && (
            <div className="bg-green-50 text-green-600 text-sm px-4 py-3 rounded-xl mb-4">{success}</div>
          )}

          {/* ── REGISTER ── */}
          {view === 'register' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <input
                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:border-blue-400"
                placeholder="Ahmad Al-Rashidi"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
              />
            </div>
          )}

          {/* ── EMAIL (all views) ── */}
          {!success && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:border-blue-400"
                placeholder="Enter your email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>
          )}

          {/* ── PASSWORD (login / register only) ── */}
          {(view === 'login' || view === 'register') && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:border-blue-400"
                placeholder="Enter your password"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') view === 'login' ? handleLogin() : handleRegister(); }}
              />
            </div>
          )}

          {/* ── COUNTRY (register only) ── */}
          {view === 'register' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
              <div className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-700">
                🇯🇴 Jordan
              </div>
            </div>
          )}

          {/* ── FORGOT PASSWORD link (login view only) ── */}
          {view === 'login' && (
            <div className="flex justify-end mb-4 -mt-2">
              <button
                onClick={() => reset('forgot')}
                className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
              >
                Forgot Password?
              </button>
            </div>
          )}

          {/* ── FORGOT: hint text ── */}
          {view === 'forgot' && !success && (
            <p className="text-sm text-gray-500 mb-4">
              Enter the email address associated with your account and we will send you a link to reset your password.
            </p>
          )}

          {/* ── PRIMARY ACTION BUTTON ── */}
          {!success && (
            <button
              onClick={
                view === 'login' ? handleLogin :
                view === 'register' ? handleRegister :
                handleForgotPassword
              }
              disabled={loading}
              className="w-full py-3 rounded-full font-semibold text-white transition-all hover:opacity-90"
              style={{ background: '#FF6B6B' }}
            >
              {loading ? 'Please wait...' :
               view === 'login' ? 'Login' :
               view === 'register' ? 'Create Account' :
               'Send Reset Link'}
            </button>
          )}

          {/* ── BACK TO LOGIN (after success) ── */}
          {view === 'forgot' && success && (
            <button
              onClick={() => reset('login')}
              className="w-full py-3 rounded-full font-semibold text-white transition-all hover:opacity-90"
              style={{ background: '#1E2A4A' }}
            >
              Back to Login
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

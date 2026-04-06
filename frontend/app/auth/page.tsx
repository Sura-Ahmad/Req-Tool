'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login, register } from '@/lib/api';

export default function AuthPage() {
  const router = useRouter();
  const [tab, setTab] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <h1 className="text-4xl font-bold text-navy mb-2" style={{color: '#1E2A4A'}}>
        Requirements Super Tool
      </h1>
      <p className="text-gray-500 mb-8">Your intelligent requirements management platform</p>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 w-full max-w-md overflow-hidden">
        {/* Tabs */}
        <div className="flex">
          <button
            onClick={() => { setTab('login'); setError(''); }}
            className="flex-1 py-4 font-semibold text-sm transition-all"
            style={{ background: tab === 'login' ? '#1E2A4A' : '#F3F4F6', color: tab === 'login' ? 'white' : '#374151', borderRadius: tab === 'login' ? '16px 16px 0 0' : '0' }}
          >Login</button>
          <button
            onClick={() => { setTab('register'); setError(''); }}
            className="flex-1 py-4 font-semibold text-sm transition-all"
            style={{ background: tab === 'register' ? '#1E2A4A' : '#F3F4F6', color: tab === 'register' ? 'white' : '#374151', borderRadius: tab === 'register' ? '16px 16px 0 0' : '0' }}
          >Register</button>
        </div>

        <div className="p-8">
          {error && <div className="bg-red-50 text-red-500 text-sm px-4 py-3 rounded-xl mb-4">{error}</div>}

          {tab === 'register' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <input className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:border-blue-400" placeholder="Ahmad Al-Rashidi" value={fullName} onChange={e => setFullName(e.target.value)} />
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:border-blue-400" placeholder="Enter your email" type="email" value={email} onChange={e => setEmail(e.target.value)} />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:border-blue-400" placeholder="Enter your password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </div>

          {tab === 'register' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
              <div className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-700">🇯🇴 Jordan</div>
            </div>
          )}

          <button
            onClick={tab === 'login' ? handleLogin : handleRegister}
            disabled={loading}
            className="w-full py-3 rounded-full font-semibold text-white transition-all hover:opacity-90"
            style={{ background: '#FF6B6B' }}
          >
            {loading ? 'Please wait...' : tab === 'login' ? 'Login' : 'Create Account'}
          </button>
        </div>
      </div>
    </div>
  );
}
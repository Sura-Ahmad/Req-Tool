'use client';
import { useEffect, useRef, useState } from 'react';
import { Camera, Trash2, Mail, User, Save } from 'lucide-react';
import { getMyProfile, updateProfile, uploadAvatar, deleteAvatar } from '@/lib/api';

const API_URL = 'http://localhost:8000';

interface Profile {
  full_name: string;
  email: string;
  avatar_url: string | null;
}

type Toast = { type: 'success' | 'error'; message: string } | null;

function getInitials(name: string) {
  return name.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2);
}

function ToastBanner({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [toast]);

  if (!toast) return null;
  const isSuccess = toast.type === 'success';
  return (
    <div
      className="fixed top-6 right-6 z-50 px-5 py-3 rounded-2xl shadow-lg text-sm font-medium text-white transition-all"
      style={{ background: isSuccess ? '#4CAF50' : '#FF6B6B' }}
    >
      {toast.message}
    </div>
  );
}

export default function EditProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [preview, setPreview] = useState<string | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<Toast>(null);
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getMyProfile().then(res => {
      setProfile(res.data);
      setFullName(res.data.full_name);
      setEmail(res.data.email);
    });
  }, []);

  const hasChanges = profile
    ? fullName.trim() !== profile.full_name || email.trim().toLowerCase() !== profile.email || !!pendingFile
    : false;

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setToast({ type: 'error', message: 'Only image files are allowed' });
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setToast({ type: 'error', message: 'File must be under 5 MB' });
      return;
    }
    setPendingFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (pendingFile) {
        setUploading(true);
        const res = await uploadAvatar(pendingFile);
        setProfile(prev => prev ? { ...prev, avatar_url: res.data.avatar_url } : prev);
        setPendingFile(null);
        setPreview(null);
        setUploading(false);
      }
      if (profile && (fullName.trim() !== profile.full_name || email.trim().toLowerCase() !== profile.email)) {
        const res = await updateProfile({ full_name: fullName.trim(), email: email.trim().toLowerCase() });
        setProfile(prev => prev ? { ...prev, full_name: res.data.full_name, email: res.data.email } : prev);
      }
      setToast({ type: 'success', message: 'Profile updated successfully' });
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Failed to update profile';
      setToast({ type: 'error', message: msg });
    } finally {
      setSaving(false);
      setUploading(false);
    }
  };

  const handleRemoveAvatar = async () => {
    try {
      await deleteAvatar();
      setProfile(prev => prev ? { ...prev, avatar_url: null } : prev);
      setPreview(null);
      setPendingFile(null);
      setToast({ type: 'success', message: 'Avatar removed' });
    } catch {
      setToast({ type: 'error', message: 'Failed to remove avatar' });
    }
  };

  const currentAvatar = preview ?? (profile?.avatar_url ? `${API_URL}${profile.avatar_url}` : null);

  return (
    <>
      <ToastBanner toast={toast} onClose={() => setToast(null)} />

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8">
        <h2 className="text-base font-semibold mb-6" style={{ color: '#1E2A4A' }}>Edit Profile</h2>

        {/* Avatar uploader */}
        <div className="flex flex-col items-center mb-8">
          <div
            className={`relative cursor-pointer rounded-full transition-all ${dragging ? 'ring-2 ring-offset-2' : ''}`}
            style={{ ringColor: '#FF6B6B' }}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
          >
            {currentAvatar ? (
              <img
                src={currentAvatar}
                alt="avatar"
                className="w-32 h-32 rounded-full object-cover border-4 border-gray-100"
              />
            ) : (
              <div
                className="w-32 h-32 rounded-full flex items-center justify-center text-white text-4xl font-bold border-4 border-gray-100"
                style={{ background: 'linear-gradient(135deg, #1E2A4A 0%, #FF6B6B 100%)' }}
              >
                {profile ? getInitials(profile.full_name) : ''}
              </div>
            )}
            {/* Camera overlay */}
            <div className="absolute inset-0 rounded-full flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-30 transition-all">
              <Camera size={24} className="text-white opacity-0 hover:opacity-100 transition-all" />
            </div>
          </div>
          <input
            ref={fileRef}
            type="file"
            accept="image/jpg,image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={e => { const f = e.target.files?.[0]; if (f) handleFileSelect(f); }}
          />
          <div className="flex gap-2 mt-3">
            <button
              onClick={() => fileRef.current?.click()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-white transition-all"
              style={{ background: '#1E2A4A' }}
            >
              <Camera size={13} />
              {currentAvatar ? 'Change Photo' : 'Upload Photo'}
            </button>
            {(profile?.avatar_url || preview) && (
              <button
                onClick={handleRemoveAvatar}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all"
                style={{ background: '#FFF0F0', color: '#FF6B6B' }}
              >
                <Trash2 size={13} />
                Remove
              </button>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1">JPG, PNG or WebP — max 5 MB. Drag & drop supported.</p>
        </div>

        {/* Form */}
        <div className="space-y-5 max-w-md">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#1E2A4A' }}>
              Full Name
            </label>
            <div className="relative">
              <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200"
                placeholder="Your full name"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#1E2A4A' }}>
              Email Address
            </label>
            <div className="relative">
              <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200"
                placeholder="your@email.com"
              />
            </div>
          </div>

          <button
            onClick={handleSave}
            disabled={!hasChanges || saving}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ background: '#FF6B6B' }}
          >
            {saving ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Save size={15} />
            )}
            {saving ? (uploading ? 'Uploading…' : 'Saving…') : 'Save Changes'}
          </button>
        </div>
      </div>
    </>
  );
}

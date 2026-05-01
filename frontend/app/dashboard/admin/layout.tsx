'use client';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { BarChart2, Users, List, Globe, Activity, Shield, BookOpen } from 'lucide-react';
import { getMe } from '@/lib/api';

const adminNav = [
  { label: 'Overview', icon: BarChart2, href: '/dashboard/admin' },
  { label: 'Users', icon: Users, href: '/dashboard/admin/users' },
  { label: 'Sessions', icon: List, href: '/dashboard/admin/sessions' },
  { label: 'Domains & Questions', icon: Globe, href: '/dashboard/admin/domains' },
  { label: 'Knowledge Base', icon: BookOpen, href: '/dashboard/admin/knowledge-base' },
  { label: 'Audit Log', icon: Activity, href: '/dashboard/admin/audit-log' },
  { label: 'Login History', icon: Shield, href: '/dashboard/admin/login-history' },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    getMe().then(res => {
      if (res.data.role !== 'admin') router.replace('/dashboard');
      else setChecked(true);
    }).catch(() => router.replace('/auth'));
  }, []);

  if (!checked) return null;

  return (
    <div className="flex h-full min-h-screen">
      {/* Admin sub-sidebar */}
      <div className="w-52 flex-shrink-0 border-r border-gray-100 bg-white py-6 px-3 flex flex-col gap-1">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-3">Admin Panel</p>
        {adminNav.map(item => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <button
              key={item.href}
              onClick={() => router.push(item.href)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all w-full text-left"
              style={{
                background: active ? '#FFF0F0' : 'transparent',
                color: active ? '#FF6B6B' : '#6B7280',
              }}
            >
              <Icon size={16} />
              {item.label}
            </button>
          );
        })}
      </div>

      {/* Admin content */}
      <div className="flex-1 overflow-auto p-8">
        {children}
      </div>
    </div>
  );
}

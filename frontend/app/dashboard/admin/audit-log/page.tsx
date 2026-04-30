'use client';
import { useEffect, useState } from 'react';
import { Activity, ChevronDown, ChevronRight, Search, Filter, ChevronLeft } from 'lucide-react';
import { getAuditLog, getUsers } from '@/lib/api';

interface AuditEntry {
  id: string;
  user_id: string | null;
  user_name: string | null;
  user_email: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

interface PageData {
  items: AuditEntry[];
  total: number;
  page: number;
  pages: number;
}

const ACTION_LABELS: Record<string, string> = {
  create_domain: 'Create Domain',
  update_domain: 'Update Domain',
  delete_domain: 'Delete Domain',
  create_question: 'Create Question',
  update_question: 'Update Question',
  delete_question: 'Delete Question',
  activate_user: 'Activate User',
  deactivate_user: 'Deactivate User',
};

const ACTION_COLORS: Record<string, string> = {
  create_domain: '#4CAF50',
  update_domain: '#2196F3',
  delete_domain: '#FF6B6B',
  create_question: '#4CAF50',
  update_question: '#2196F3',
  delete_question: '#FF6B6B',
  activate_user: '#4CAF50',
  deactivate_user: '#FF6B6B',
};

export default function AuditLogPage() {
  const [data, setData] = useState<PageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const [filterUserId, setFilterUserId] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');
  const [users, setUsers] = useState<{ id: string; full_name: string; email: string }[]>([]);

  const fetchData = async (p = page) => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = { page: p, limit: 20 };
      if (filterUserId) params.user_id = filterUserId;
      if (filterAction) params.action = filterAction;
      if (filterDateFrom) params.date_from = filterDateFrom;
      if (filterDateTo) params.date_to = filterDateTo;
      const res = await getAuditLog(params);
      setData(res.data);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getUsers().then(res => setUsers(res.data.filter((u: { role: string }) => u.role === 'admin'))).catch(() => {});
  }, []);

  useEffect(() => {
    fetchData(page);
  }, [page]);

  const handleFilter = () => {
    setPage(1);
    fetchData(1);
  };

  const handleReset = () => {
    setFilterUserId('');
    setFilterAction('');
    setFilterDateFrom('');
    setFilterDateTo('');
    setPage(1);
    setTimeout(() => fetchData(1), 0);
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: '#FFF0F0' }}>
          <Activity size={20} style={{ color: '#FF6B6B' }} />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#1E2A4A' }}>Audit Log</h1>
          <p className="text-sm text-gray-500">Track all admin actions across the system</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter size={15} style={{ color: '#6B7280' }} />
          <span className="text-sm font-medium text-gray-600">Filters</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <select
            value={filterUserId}
            onChange={e => setFilterUserId(e.target.value)}
            className="text-sm border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-200"
          >
            <option value="">All Users</option>
            {users.map(u => (
              <option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>
            ))}
          </select>

          <select
            value={filterAction}
            onChange={e => setFilterAction(e.target.value)}
            className="text-sm border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-200"
          >
            <option value="">All Actions</option>
            {Object.entries(ACTION_LABELS).map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </select>

          <input
            type="date"
            value={filterDateFrom}
            onChange={e => setFilterDateFrom(e.target.value)}
            className="text-sm border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-200"
            placeholder="From date"
          />

          <input
            type="date"
            value={filterDateTo}
            onChange={e => setFilterDateTo(e.target.value)}
            className="text-sm border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-200"
            placeholder="To date"
          />
        </div>
        <div className="flex gap-2 mt-3">
          <button
            onClick={handleFilter}
            className="px-4 py-2 rounded-xl text-sm font-medium text-white transition-all"
            style={{ background: '#FF6B6B' }}
          >
            Apply Filters
          </button>
          <button
            onClick={handleReset}
            className="px-4 py-2 rounded-xl text-sm font-medium transition-all"
            style={{ background: '#F3F4F6', color: '#6B7280' }}
          >
            Reset
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: '#FF6B6B', borderTopColor: 'transparent' }} />
          </div>
        ) : !data || data.items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <Activity size={40} className="mb-3 opacity-30" />
            <p className="text-sm">No audit log entries found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ background: '#F9FAFB' }}>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Timestamp</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">User</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Action</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Entity Type</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Entity ID</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">IP Address</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Details</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((entry, idx) => (
                  <>
                    <tr
                      key={entry.id}
                      className="border-t border-gray-50 hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => setExpandedRow(expandedRow === entry.id ? null : entry.id)}
                    >
                      <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                        {new Date(entry.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        {entry.user_name ? (
                          <div>
                            <div className="font-medium" style={{ color: '#1E2A4A' }}>{entry.user_name}</div>
                            <div className="text-xs text-gray-400">{entry.user_email}</div>
                          </div>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="px-2 py-1 rounded-lg text-xs font-medium text-white"
                          style={{ background: ACTION_COLORS[entry.action] || '#6B7280' }}
                        >
                          {ACTION_LABELS[entry.action] || entry.action}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600 capitalize">{entry.entity_type}</td>
                      <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                        {entry.entity_id ? entry.entity_id.slice(0, 8) + '…' : '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-500 font-mono text-xs">{entry.ip_address || '—'}</td>
                      <td className="px-4 py-3">
                        {entry.details ? (
                          <span className="flex items-center gap-1 text-xs" style={{ color: '#FF6B6B' }}>
                            {expandedRow === entry.id ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                            View
                          </span>
                        ) : (
                          <span className="text-gray-400 text-xs">—</span>
                        )}
                      </td>
                    </tr>
                    {expandedRow === entry.id && entry.details && (
                      <tr key={`${entry.id}-detail`} className="border-t border-gray-50">
                        <td colSpan={7} className="px-4 py-3" style={{ background: '#F9FAFB' }}>
                          <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono bg-white rounded-xl p-3 border border-gray-100 overflow-auto max-h-48">
                            {JSON.stringify(entry.details, null, 2)}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {data && data.pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
            <span className="text-sm text-gray-500">
              Showing {((page - 1) * 20) + 1}–{Math.min(page * 20, data.total)} of {data.total}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-sm font-medium" style={{ color: '#1E2A4A' }}>
                {page} / {data.pages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(data.pages, p + 1))}
                disabled={page === data.pages}
                className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

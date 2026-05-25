'use client';
import { useEffect, useState } from 'react';
import { getDocuments, getDocument } from '@/lib/api';
import { Download } from 'lucide-react';

interface DocumentRow {
  session_id: string;
  user_name: string;
  user_email: string;
  domain: string;
  country: string;
  created_at: string | null;
  preview: string;
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    getDocuments().then(res => setDocs(res.data)).finally(() => setLoading(false));
  }, []);

  const fmt = (iso: string | null) =>
    iso ? new Date(iso).toLocaleString() : '—';

  const handleDownload = async (sessionId: string, userEmail: string) => {
    setDownloading(sessionId);
    try {
      const res = await getDocument(sessionId);
      const text = res.data.document_text;
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document_${userEmail}_${sessionId.slice(0, 8)}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <>
      <h1 className="text-2xl font-bold mb-1" style={{ color: '#1E2A4A' }}>User Uploaded Documents</h1>
      <p className="text-gray-500 mb-6">PII-cleaned documents submitted by users during requirements generation</p>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="w-8 h-8 border-4 border-gray-200 rounded-full animate-spin" style={{ borderTopColor: '#FF6B6B' }} />
        </div>
      ) : docs.length === 0 ? (
        <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center text-gray-400">
          No documents uploaded yet.
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Domain</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Country</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Date</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Preview</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Download</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc, i) => (
                <tr key={doc.session_id} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{doc.user_name}</div>
                    <div className="text-xs text-gray-400">{doc.user_email}</div>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{doc.domain}</td>
                  <td className="px-4 py-3 text-gray-600">{doc.country}</td>
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{fmt(doc.created_at)}</td>
                  <td className="px-4 py-3 text-gray-500 max-w-xs">
                    <p className="truncate text-xs">{doc.preview}</p>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleDownload(doc.session_id, doc.user_email)}
                      disabled={downloading === doc.session_id}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                      style={{ background: '#FFF0F0', color: '#FF6B6B' }}
                    >
                      <Download size={13} />
                      {downloading === doc.session_id ? 'Downloading...' : 'Download'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

'use client';
import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { generateRequirements, getRequirements, updateRequirement, crossCheck, generateSRS, generateUseCases } from '@/lib/api';
import { Pencil, Check, X, Download } from 'lucide-react';
import { generateAndDownloadSRSWord, generateAndDownloadUseCasesWord } from '@/lib/generateSRSWord';

const TABS = ['Functional Requirements', 'Non-Functional Requirements', 'Use Cases', 'Full SRS'];

export default function RequirementsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get('session_id') || '';
  const documentText = searchParams.get('document_text') || '';

  const [tab, setTab] = useState(0);
  const [functional, setFunctional] = useState<any[]>([]);
  const [nonFunctional, setNonFunctional] = useState<any[]>([]);
  const [useCases, setUseCases] = useState<any[]>([]);
  const [srs, setSrs] = useState('');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [issues, setIssues] = useState<any[]>([]);
  const [crossChecking, setCrossChecking] = useState(false);
  const [error, setError] = useState('');

  const hasGenerated = useRef(false);

  useEffect(() => {
    if (!sessionId) {
      router.replace('/dashboard');
      return;
    }
    if (!hasGenerated.current) {
      hasGenerated.current = true;
      generateReqs();
    }
  }, [sessionId]);

  const generateReqs = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await generateRequirements(sessionId, documentText);
      setFunctional(res.data.functional);
      setNonFunctional(res.data.non_functional);
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || 'Error generating requirements';
      setError(errorMsg);
    } finally { setLoading(false); }
  };

  const handleEdit = (req: any) => {
    setEditingId(req.id);
    setEditText(req.description);
  };

  const handleSaveEdit = async (id: string) => {
    await updateRequirement(id, editText);
    setFunctional(functional.map(r => r.id === id ? { ...r, description: editText } : r));
    setNonFunctional(nonFunctional.map(r => r.id === id ? { ...r, description: editText } : r));
    setEditingId(null);
  };

  const handleCrossCheck = async () => {
    setCrossChecking(true);
    try {
      const res = await crossCheck(sessionId);
      setIssues(res.data.issues);
    } finally { setCrossChecking(false); }
  };

  const handleGenerateUseCases = async () => {
    setGenerating(true);
    try {
      const res = await generateUseCases(sessionId);
      setUseCases(res.data.use_cases);
      setTab(2);
    } finally { setGenerating(false); }
  };

  const handleGenerateSRS = async () => {
    setGenerating(true);
    try {
      const res = await generateSRS(sessionId, 'My Project');
      setSrs(res.data.content);
      setTab(3);
    } finally { setGenerating(false); }
  };

  const handleDownloadWord = () =>
    generateAndDownloadSRSWord(srs, functional, nonFunctional, 'My Project');

  const handleDownloadUseCasesWord = () =>
    generateAndDownloadUseCasesWord(useCases, 'My Project');

  const getIssueColor = (reqId: string) => {
    const issue = issues.find(i => i.requirement_id === reqId);
    return issue ? issue.highlight_color : null;
  };

  const RequirementCard = ({ req }: { req: any }) => {
    const issueColor = getIssueColor(req.id);
    return (
      <div className="bg-white rounded-2xl border p-5 mb-3 transition-all"
        style={{ borderColor: issueColor || '#E5E7EB', borderLeftWidth: issueColor ? '4px' : '1px' }}>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <span className="font-bold text-gray-800 text-sm">{req.code}</span>
            {editingId === req.id ? (
              <div className="mt-2">
                <textarea className="w-full px-3 py-2 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none text-sm resize-none" rows={3}
                  value={editText} onChange={e => setEditText(e.target.value)} />
                <div className="flex gap-2 mt-2">
                  <button onClick={() => handleSaveEdit(req.id)} className="flex items-center gap-1 px-3 py-1 rounded-full text-xs text-white" style={{ background: '#4CAF50' }}>
                    <Check size={12} /> Save
                  </button>
                  <button onClick={() => setEditingId(null)} className="flex items-center gap-1 px-3 py-1 rounded-full text-xs text-white" style={{ background: '#9CA3AF' }}>
                    <X size={12} /> Cancel
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-gray-600 text-sm mt-1">{req.description}</p>
            )}
          </div>
          {editingId !== req.id && (
            <button onClick={() => handleEdit(req)} className="ml-3 text-gray-400 hover:text-gray-600">
              <Pencil size={16} />
            </button>
          )}
        </div>
        {issueColor && (() => {
  const issue = issues.find(i => i.requirement_id === req.id);
  return (
    <div className="mt-2">
      <div className="text-xs px-2 py-1 rounded-full inline-block text-white mb-2"
        style={{ background: issueColor }}>
        {issue?.issue_type}
      </div>
      {issue?.issue_detail && (
        <p className="text-xs text-gray-600 mt-1">
          <span className="font-medium">Detail:</span> {issue.issue_detail}
        </p>
      )}
      {issue?.conflict_with && (
        <p className="text-xs text-gray-500 mt-1">
          <span className="font-medium">Conflicts with:</span> {issue.conflict_with}
        </p>
      )}
    </div>
  );
})()}
      </div>
    );
  };

  return (
    <div className="flex h-screen">
      {/* Left Sidebar */}
      <div className="w-64 bg-white border-r border-gray-100 p-6 flex flex-col gap-6">
        <div>
          <h3 className="font-semibold text-gray-800 mb-3">Session Info</h3>
          <div className="flex flex-col gap-2 text-sm">
            <div><span className="text-gray-400">Domain:</span><p className="font-medium">Health</p></div>
            <div><span className="text-gray-400">Role:</span><p className="font-medium">Business Analyst</p></div>
            <div><span className="text-gray-400">Country:</span><p className="font-medium">Jordan</p></div>
            <div><span className="text-gray-400">Created:</span><p className="font-medium">{new Date().toLocaleDateString()}</p></div>
          </div>
        </div>

        <button onClick={handleCrossCheck} disabled={crossChecking}
          className="w-full py-3 rounded-xl text-white font-medium text-sm transition-all hover:opacity-90"
          style={{ background: '#FF6B6B' }}>
          {crossChecking ? 'Checking...' : 'Run Cross-Check'}
        </button>

        {issues.length > 0 && (
  <div className="text-xs">
    <p className="font-medium text-gray-700 mb-2">Legend:</p>
    {[
      { color: '#FFA500', label: 'Ambiguity' },
      { color: '#FF6B6B', label: 'Duplicate' },
      { color: '#9B59B6', label: 'Inconsistency' },
      { color: '#FF0000', label: 'Conflict' },
      { color: '#3498DB', label: 'Unsupported' }
    ].map(i => (
      <div key={i.label} className="flex items-center gap-2 mb-1">
        <div className="w-3 h-3 rounded-full" style={{ background: i.color }} />
        <span className="text-gray-600">{i.label}</span>
      </div>
    ))}
  </div>
)}

        <div>
          <p className="font-medium text-gray-700 mb-2 text-sm">Export</p>
          <button onClick={handleGenerateSRS} disabled={generating}
            className="w-full py-3 rounded-xl text-white font-medium text-sm transition-all hover:opacity-90 mb-2"
            style={{ background: '#FF6B6B' }}>
            {generating ? 'Generating...' : 'Generate SRS'}
          </button>
          <button onClick={handleGenerateUseCases} disabled={generating}
            className="w-full py-3 rounded-xl text-white font-medium text-sm transition-all hover:opacity-90"
            style={{ background: '#FF6B6B' }}>
            {generating ? 'Generating...' : 'Generate Use Cases'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-8">
        <h1 className="text-2xl font-bold mb-1" style={{ color: '#1E2A4A' }}>Requirements Dashboard</h1>
        <p className="text-gray-500 mb-6">View and manage your generated requirements</p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-4">
            ⚠️ {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b border-gray-100 mb-6">
          {TABS.map((t, i) => (
            <button key={i} onClick={() => setTab(i)}
              className="px-4 py-3 text-sm font-medium transition-all border-b-2"
              style={{ borderColor: tab === i ? '#FF6B6B' : 'transparent', color: tab === i ? '#FF6B6B' : '#6B7280' }}>
              {t}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="w-8 h-8 border-4 border-gray-200 rounded-full animate-spin mx-auto mb-3" style={{ borderTopColor: '#FF6B6B' }} />
              <p className="text-gray-500 text-sm">Generating requirements with AI...</p>
            </div>
          </div>
        ) : (
          <>
            {tab === 0 && functional.map(r => <RequirementCard key={r.id} req={r} />)}
            {tab === 1 && nonFunctional.map(r => <RequirementCard key={r.id} req={r} />)}
            {tab === 2 && (
              useCases.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  <p>Click "Generate Use Cases" to generate use cases</p>
                </div>
              ) : (
                <>
                  <div className="flex justify-end mb-4">
                    <button
                      onClick={handleDownloadUseCasesWord}
                      className="flex items-center gap-2 px-5 py-2 rounded-full text-white text-sm font-medium transition-all hover:opacity-90"
                      style={{ background: '#1E2A4A' }}
                    >
                      <Download size={16} /> Download as Word
                    </button>
                  </div>
                  {useCases.map((uc, i) => (
                    <div key={i} className="bg-white rounded-2xl border border-gray-100 p-5 mb-3">
                      <h3 className="font-bold text-gray-800 mb-2">{uc.title}</h3>
                      <p className="text-sm text-gray-500 mb-1"><span className="font-medium">Actor:</span> {uc.actor}</p>
                      <p className="text-sm text-gray-500 mb-1"><span className="font-medium">Preconditions:</span> {uc.preconditions}</p>
                      <p className="text-sm text-gray-500 mb-1"><span className="font-medium">Main Flow:</span> {uc.main_flow}</p>
                      <p className="text-sm text-gray-500"><span className="font-medium">Postconditions:</span> {uc.postconditions}</p>
                    </div>
                  ))}
                </>
              )
            )}
            {tab === 3 && (
              srs ? (
                <div className="bg-white rounded-2xl border border-gray-100 p-6">
                  <div className="flex justify-end mb-4">
                    <button
                      onClick={handleDownloadWord}
                      className="flex items-center gap-2 px-5 py-2 rounded-full text-white text-sm font-medium transition-all hover:opacity-90"
                      style={{ background: '#1E2A4A' }}
                    >
                      <Download size={16} /> Download as Word
                    </button>
                  </div>
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">{srs}</pre>
                </div>
              ) : (
                <div className="text-center py-16 text-gray-400">
                  <p>Click "Download SRS" to generate the SRS document</p>
                </div>
              )
            )}
          </>
        )}
      </div>
    </div>
  );
}
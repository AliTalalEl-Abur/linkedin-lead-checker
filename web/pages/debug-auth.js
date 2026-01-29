import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://linkedin-lead-checker-api.onrender.com';

export default function DebugAuth() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('');
  const [responseText, setResponseText] = useState('');
  const [errorText, setErrorText] = useState('');
  const [proxyStatus, setProxyStatus] = useState('');
  const [proxyResponseText, setProxyResponseText] = useState('');
  const [proxyErrorText, setProxyErrorText] = useState('');
  const [healthStatus, setHealthStatus] = useState('');
  const [healthResponseText, setHealthResponseText] = useState('');
  const [healthErrorText, setHealthErrorText] = useState('');
  const [loading, setLoading] = useState(false);
  const [proxyLoading, setProxyLoading] = useState(false);
  const [healthLoading, setHealthLoading] = useState(false);

  const handleTest = async (e) => {
    e.preventDefault();
    setStatus('');
    setResponseText('');
    setErrorText('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      setStatus(`HTTP ${res.status}`);
      const text = await res.text();
      setResponseText(text);
    } catch (err) {
      setErrorText(err?.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleProxyTest = async (e) => {
    e.preventDefault();
    setProxyStatus('');
    setProxyResponseText('');
    setProxyErrorText('');
    setProxyLoading(true);

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      setProxyStatus(`HTTP ${res.status}`);
      const text = await res.text();
      setProxyResponseText(text);
    } catch (err) {
      setProxyErrorText(err?.message || String(err));
    } finally {
      setProxyLoading(false);
    }
  };

  const handleHealthTest = async (e) => {
    e.preventDefault();
    setHealthStatus('');
    setHealthResponseText('');
    setHealthErrorText('');
    setHealthLoading(true);

    try {
      const res = await fetch('/api/debug/health');
      setHealthStatus(`HTTP ${res.status}`);
      const text = await res.text();
      setHealthResponseText(text);
    } catch (err) {
      setHealthErrorText(err?.message || String(err));
    } finally {
      setHealthLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 720, margin: '40px auto', fontFamily: 'system-ui' }}>
      <h1>Debug Auth</h1>
      <p><strong>API_URL:</strong> {API_URL}</p>
      <p><strong>Proxy URL:</strong> {typeof window === 'undefined' ? '' : `${window.location.origin}/api/auth/login`}</p>
      <form onSubmit={handleTest}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 6, marginBottom: 12 }}
          />
        </label>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button type="submit" disabled={loading}>
            {loading ? 'Testing direct...' : 'Test direct /auth/login'}
          </button>
          <button type="button" onClick={handleProxyTest} disabled={proxyLoading}>
            {proxyLoading ? 'Testing proxy...' : 'Test proxy /api/auth/login'}
          </button>
          <button type="button" onClick={handleHealthTest} disabled={healthLoading}>
            {healthLoading ? 'Testing health...' : 'Test proxy /health'}
          </button>
        </div>
      </form>

      {status && (
        <p><strong>Status:</strong> {status}</p>
      )}
      {responseText && (
        <pre style={{ background: '#111', color: '#0f0', padding: 12, overflow: 'auto' }}>{responseText}</pre>
      )}
      {errorText && (
        <pre style={{ background: '#111', color: '#f66', padding: 12, overflow: 'auto' }}>{errorText}</pre>
      )}

      <hr style={{ margin: '24px 0' }} />

      {proxyStatus && (
        <p><strong>Proxy Status:</strong> {proxyStatus}</p>
      )}
      {proxyResponseText && (
        <pre style={{ background: '#111', color: '#0ff', padding: 12, overflow: 'auto' }}>{proxyResponseText}</pre>
      )}
      {proxyErrorText && (
        <pre style={{ background: '#111', color: '#f66', padding: 12, overflow: 'auto' }}>{proxyErrorText}</pre>
      )}

      {healthStatus && (
        <p><strong>Health Status:</strong> {healthStatus}</p>
      )}
      {healthResponseText && (
        <pre style={{ background: '#111', color: '#ff0', padding: 12, overflow: 'auto' }}>{healthResponseText}</pre>
      )}
      {healthErrorText && (
        <pre style={{ background: '#111', color: '#f66', padding: 12, overflow: 'auto' }}>{healthErrorText}</pre>
      )}
    </main>
  );
}

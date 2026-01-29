import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/Dashboard.module.css';
import { authenticatedFetch, getStoredToken, clearToken } from '../lib/api';

export default function Upgrade() {
  const router = useRouter();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || '';
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is authenticated
    const token = getStoredToken();
    if (!token) {
      window.location.href = `${siteUrl}/login`;
    }
  }, [router]);

  const handleUpgrade = async () => {
    setLoading(true);
    setError('');

    try {
      // Get return URL from environment (required in production)
      const returnUrl = process.env.NEXT_PUBLIC_CHECKOUT_RETURN_URL;
      if (!returnUrl) {
        throw new Error('NEXT_PUBLIC_CHECKOUT_RETURN_URL is not set');
      }

      const data = await authenticatedFetch('/billing/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ return_url: returnUrl }),
      });
      
      // Redirect to Stripe checkout
      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong';
      if (message.includes('Session expired') || message.includes('Not authenticated')) {
        clearToken();
        window.location.href = `${siteUrl}/login`;
        return;
      }
      setError(message);
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1>Upgrade to Pro</h1>
        <p>Unlock unlimited profile analysis and advanced features.</p>
        
        <div className={styles.features}>
          <h3>Pro Plan Includes:</h3>
          <ul>
            <li>500 analyses per week (vs 5 for free)</li>
            <li>Advanced filtering by industry and seniority</li>
            <li>Priority support</li>
            <li>Custom ICP configuration</li>
          </ul>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <button 
          onClick={handleUpgrade} 
          disabled={loading}
          className={styles.primaryButton}
        >
          {loading ? 'Processing...' : 'Upgrade Now'}
        </button>

        <button 
          onClick={() => window.location.href = `${siteUrl}/dashboard`}
          className={styles.secondaryButton}
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/Dashboard.module.css';
import { authenticatedFetch, getStoredToken, clearToken } from '../lib/api';

export default function Upgrade() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is authenticated
    const token = getStoredToken();
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleUpgrade = async () => {
    setLoading(true);
    setError('');

    try {
      // Get return URL from environment or construct from current location
      const returnUrl = process.env.NEXT_PUBLIC_CHECKOUT_RETURN_URL || 
        `${typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'}/checkout-result?session_id={CHECKOUT_SESSION_ID}`;

      const response = await authenticatedFetch('/billing/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ return_url: returnUrl }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          clearToken();
          router.push('/login');
          return;
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create checkout session');
      }

      const data = await response.json();
      
      // Redirect to Stripe checkout
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
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
          onClick={() => router.push('/dashboard')}
          className={styles.secondaryButton}
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { getStoredToken, clearToken, authenticatedFetch } from '../lib/api';
import styles from '../styles/Dashboard.module.css';

export default function DashboardPage() {
  const router = useRouter();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || '';
  const [loading, setLoading] = useState(true);
  const [userPlan, setUserPlan] = useState('free');
  const [usageStats, setUsageStats] = useState(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      window.location.href = `${siteUrl}/login`;
    } else {
      fetchUserProfile();
    }
  }, [router]);

  const fetchUserProfile = async () => {
    try {
      const response = await authenticatedFetch('/user', {
        method: 'GET',
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserPlan(data.plan);
        setUsageStats(data.usage_stats);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    clearToken();
    window.location.href = `${siteUrl}/login`;
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>📊 Dashboard</h1>
        <button onClick={handleLogout} className={styles.logoutBtn}>
          Logout
        </button>
      </div>

      <div className={styles.card}>
        <h2>✅ Setup Complete!</h2>
        <p>Your ICP configuration has been saved.</p>
        
        <div className={styles.planStatus}>
          <h3>Your Plan: <span className={userPlan === 'pro' ? styles.proBadge : styles.freeBadge}>
            {userPlan.toUpperCase()}
          </span></h3>
          {usageStats && (
            <div className={styles.usageInfo}>
              <p>Analyses this week: {usageStats.usage_count || 0} / {userPlan === 'pro' ? 500 : 5}</p>
            </div>
          )}
        </div>

        {userPlan === 'free' && (
          <button 
            onClick={() => window.location.href = `${siteUrl}/upgrade`}
            className={styles.upgradeButton}
          >
            🚀 Upgrade to Pro
          </button>
        )}

        <div className={styles.nextSteps}>
          <h3>Next Steps:</h3>
          <ol>
            <li>Install the Chrome extension (see README in extension/)</li>
            <li>Go to any LinkedIn profile (linkedin.com/in/someone/)</li>
            <li>Click the extension icon and analyze profiles</li>
            <li>Profiles will be scored based on your ICP</li>
          </ol>
        </div>


        <button
          onClick={() => window.location.href = `${siteUrl}/onboarding`}
          className={styles.secondaryBtn}
        >
          Edit ICP
        </button>
      </div>
    </div>
  );
}

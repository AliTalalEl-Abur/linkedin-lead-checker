import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/Dashboard.module.css';

export default function CheckoutResult() {
  const router = useRouter();
  const { session_id, status } = router.query;
  const [message, setMessage] = useState('Processing your payment...');
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    if (!session_id || !status) return;

    if (status === 'success') {
      setMessage('✅ Payment successful! Your account has been upgraded to Pro.');
      setIsSuccess(true);
      // Redirect to dashboard after 3 seconds
      setTimeout(() => router.push('/dashboard'), 3000);
    } else if (status === 'cancel') {
      setMessage('❌ Payment cancelled. Your account remains on the Free plan.');
      setIsSuccess(false);
      // Redirect to dashboard after 3 seconds
      setTimeout(() => router.push('/dashboard'), 3000);
    }
  }, [session_id, status, router]);

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1>Checkout Result</h1>
        <p className={isSuccess ? styles.success : styles.error}>
          {message}
        </p>
        <p style={{ marginTop: '20px', fontSize: '0.9em', color: '#666' }}>
          Redirecting to dashboard...
        </p>
      </div>
    </div>
  );
}

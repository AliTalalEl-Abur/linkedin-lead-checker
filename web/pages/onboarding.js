import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { getStoredToken, saveICP, clearToken } from '../lib/api';
import styles from '../styles/Onboarding.module.css';

export default function OnboardingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [form, setForm] = useState({
    oferta: '',
    roles_objetivo: [],
    roles_a_evitar: [],
    target_industries: [],
    company_size_min: '',
    company_size_max: '',
  });

  // Role options
  const roleOptions = [
    'VP',
    'Director',
    'Manager',
    'Head of',
    'C-Level',
    'Founder',
    'CEO',
    'CTO',
    'CFO',
    'COO',
    'Sales Director',
    'Product Manager',
    'Engineering Lead',
  ];

  // Industry options
  const industryOptions = [
    'Technology',
    'SaaS',
    'Finance',
    'Healthcare',
    'Retail',
    'Manufacturing',
    'Consulting',
    'Marketing',
    'Real Estate',
    'Education',
    'Telecommunications',
    'Transportation',
  ];

  // Check authentication on mount
  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      router.push('/login');
    } else {
      setLoading(false);
    }
  }, [router]);

  const handleTextChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleNumberChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value ? parseInt(value) : '' }));
  };

  const toggleMultiSelect = (field, value) => {
    setForm((prev) => {
      const arr = prev[field] || [];
      if (arr.includes(value)) {
        return { ...prev, [field]: arr.filter((v) => v !== value) };
      } else {
        return { ...prev, [field]: [...arr, value] };
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!form.oferta.trim()) {
      setError('Please enter your value proposition/offer');
      return;
    }

    if (form.roles_objetivo.length === 0) {
      setError('Please select at least one target role');
      return;
    }

    if (form.target_industries.length === 0) {
      setError('Please select at least one industry');
      return;
    }

    setSaving(true);

    try {
      const icpConfig = {
        target_industries: form.target_industries,
        target_seniority: form.roles_objetivo,
        exclude_keywords: form.roles_a_evitar.length > 0 ? form.roles_a_evitar : null,
        company_size_min: form.company_size_min || null,
        company_size_max: form.company_size_max || null,
        // Store offer as well (might need backend update)
        _offer: form.oferta,
      };

      await saveICP(icpConfig);
      setSuccess('✅ ICP configuration saved successfully!');

      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err) {
      console.error('Save error:', err);
      if (err.message.includes('Session expired')) {
        clearToken();
        router.push('/login');
      } else {
        setError(err.message || 'Failed to save ICP configuration');
      }
      setSaving(false);
    }
  };

  const handleLogout = () => {
    clearToken();
    router.push('/login');
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🎯 Configure Your ICP</h1>
        <button onClick={handleLogout} className={styles.logoutBtn}>
          Logout
        </button>
      </div>

      <div className={styles.card}>
        <p className={styles.subtitle}>
          Tell us about your ideal customer profile. This helps us score leads more accurately.
        </p>

        {error && <div className={styles.error}>{error}</div>}
        {success && <div className={styles.success}>{success}</div>}

        <form onSubmit={handleSubmit}>
          {/* Value Proposition / Offer */}
          <div className={styles.formGroup}>
            <label htmlFor="oferta">Your Value Proposition</label>
            <textarea
              id="oferta"
              name="oferta"
              placeholder="Describe what you sell or your unique value proposition (e.g., 'Enterprise SaaS for HR departments')"
              value={form.oferta}
              onChange={handleTextChange}
              disabled={saving}
              rows="3"
            />
          </div>

          {/* Target Roles */}
          <div className={styles.formGroup}>
            <label>Target Job Titles / Seniority</label>
            <div className={styles.checkboxGroup}>
              {roleOptions.map((role) => (
                <label key={role} className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={form.roles_objetivo.includes(role)}
                    onChange={() => toggleMultiSelect('roles_objetivo', role)}
                    disabled={saving}
                  />
                  {role}
                </label>
              ))}
            </div>
          </div>

          {/* Roles to Avoid */}
          <div className={styles.formGroup}>
            <label>Roles to Avoid (Optional)</label>
            <div className={styles.checkboxGroup}>
              {roleOptions.map((role) => (
                <label key={`avoid-${role}`} className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={form.roles_a_evitar.includes(role)}
                    onChange={() => toggleMultiSelect('roles_a_evitar', role)}
                    disabled={saving}
                  />
                  {role}
                </label>
              ))}
            </div>
          </div>

          {/* Target Industries */}
          <div className={styles.formGroup}>
            <label>Target Industries</label>
            <div className={styles.checkboxGroup}>
              {industryOptions.map((industry) => (
                <label key={industry} className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={form.target_industries.includes(industry)}
                    onChange={() => toggleMultiSelect('target_industries', industry)}
                    disabled={saving}
                  />
                  {industry}
                </label>
              ))}
            </div>
          </div>

          {/* Company Size Range */}
          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="company_size_min">Min Company Size (employees)</label>
              <input
                id="company_size_min"
                type="number"
                name="company_size_min"
                placeholder="e.g., 50"
                value={form.company_size_min}
                onChange={handleNumberChange}
                disabled={saving}
                min="0"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="company_size_max">Max Company Size (employees)</label>
              <input
                id="company_size_max"
                type="number"
                name="company_size_max"
                placeholder="e.g., 5000"
                value={form.company_size_max}
                onChange={handleNumberChange}
                disabled={saving}
                min="0"
              />
            </div>
          </div>

          <button
            type="submit"
            className={styles.primaryBtn}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save ICP Configuration'}
          </button>
        </form>
      </div>
    </div>
  );
}

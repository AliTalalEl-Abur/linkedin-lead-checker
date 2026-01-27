import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { authenticatedFetch, getStoredToken } from '../../lib/api';
import { useChromeExtension, isChromeBrowser, getChromeWebStoreUrl } from '../../lib/extension';
import Button from '../../components/Button';
import styles from '../../styles/Dashboard.module.css';

export default function BillingSuccess() {
  const router = useRouter();
  const { session_id } = router.query;
  const { isInstalled, isChecking, openExtension } = useChromeExtension();
  const [showInstructions, setShowInstructions] = useState(false);
  const [status, setStatus] = useState({
    loading: true,
    plan: null,
    error: null,
    billingInfo: null
  });

  useEffect(() => {
    // Verificar que el usuario esté autenticado
    const token = getStoredToken();
    if (!token) {
      router.push('/login');
      return;
    }

    // Obtener información de facturación
    const fetchBillingStatus = async () => {
      try {
        const billingData = await authenticatedFetch('/billing/status', {
          method: 'GET'
        });

        setStatus({
          loading: false,
          plan: billingData.plan,
          error: null,
          billingInfo: billingData
        });
      } catch (error) {
        console.error('Error fetching billing status:', error);
        setStatus({
          loading: false,
          plan: null,
          error: 'Failed to load billing information',
          billingInfo: null
        });
      }
    };

    if (router.isReady && session_id) {
      // Pequeño delay para dar tiempo a que el webhook procese
      setTimeout(fetchBillingStatus, 2000);
    }
  }, [router.isReady, session_id, router]);

  const handleBackToExtension = () => {
    // Try to close the tab first (works if opened by extension)
    if (window.opener) {
      window.close();
      return;
    }

    // If extension is installed, try to open it
    if (isInstalled) {
      openExtension()
        .then(() => {
          // Success - show message and try to close tab
          setTimeout(() => {
            window.close();
          }, 1000);
        })
        .catch((error) => {
          console.error('Failed to open extension:', error);
          // Show manual instructions
          setShowInstructions(true);
        });
    } else {
      // Extension not installed, show instructions
      setShowInstructions(true);
    }
  };

  const handleGoToDashboard = () => {
    router.push('/dashboard');
  };

  if (status.loading) {
    return (
      <>
        <Head>
          <title>Processing Payment - LinkedIn Lead Checker</title>
        </Head>
        <div className={styles.container}>
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <h1 className="text-2xl font-bold text-gray-800 mb-2">Processing your payment...</h1>
              <p className="text-gray-600">Please wait while we confirm your subscription.</p>
            </div>
          </div>
        </div>
      </>
    );
  }

  if (status.error) {
    return (
      <>
        <Head>
          <title>Payment Error - LinkedIn Lead Checker</title>
        </Head>
        <div className={styles.container}>
          <div className="min-h-screen flex items-center justify-center">
            <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
              <div className="text-red-500 text-5xl mb-4">⚠️</div>
              <h1 className="text-2xl font-bold text-gray-800 mb-4">Something went wrong</h1>
              <p className="text-gray-600 mb-6">{status.error}</p>
              <Button variant="primary" onClick={handleGoToDashboard}>
                Go to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </>
    );
  }

  const getPlanDisplay = (plan) => {
    const plans = {
      starter: { name: 'Starter', color: 'text-green-600', limit: '40 analyses/month' },
      pro: { name: 'Pro', color: 'text-blue-600', limit: '150 analyses/month' },
      team: { name: 'Team', color: 'text-purple-600', limit: '500 analyses/month' }
    };
    return plans[plan] || { name: plan, color: 'text-gray-600', limit: '' };
  };

  const planInfo = getPlanDisplay(status.plan);
  const isActivePlan = ['starter', 'pro', 'team'].includes(status.plan);

  return (
    <>
      <Head>
        <title>Payment Successful - LinkedIn Lead Checker</title>
        <meta name="robots" content="noindex" />
      </Head>
      <div className={styles.container}>
        <div className="min-h-screen flex items-center justify-center py-12 px-4">
          <div className="max-w-lg w-full bg-white rounded-lg shadow-xl p-8">
            {/* Success Icon */}
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Payment Successful!
              </h1>
              <p className="text-gray-600">
                Your subscription has been activated
              </p>
            </div>

            {/* Plan Information */}
            {isActivePlan && status.billingInfo && (
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-600 font-medium">Active Plan</span>
                  <span className={`text-xl font-bold ${planInfo.color}`}>
                    {planInfo.name}
                  </span>
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly Limit</span>
                    <span className="font-semibold text-gray-900">
                      {status.billingInfo.usage_limit} analyses
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Used This Month</span>
                    <span className="font-semibold text-gray-900">
                      {status.billingInfo.usage_current} / {status.billingInfo.usage_limit}
                    </span>
                  </div>
                  
                  {status.billingInfo.reset_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Renews On</span>
                      <span className="font-semibold text-gray-900">
                        {new Date(status.billingInfo.reset_date).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex justify-between pt-3 border-t border-gray-200">
                    <span className="text-gray-600">Status</span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Active
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Success Message */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800">
                <strong>🎉 You're all set!</strong> You can now use the extension to analyze {status.billingInfo?.usage_limit || 'unlimited'} LinkedIn profiles per month.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              {!isChecking && (
                <>
                  <Button 
                    variant="primary" 
                    onClick={handleBackToExtension}
                    className="w-full"
                  >
                    {isInstalled ? 'Back to Extension' : 'Open Extension'}
                  </Button>
                  
                  {!isInstalled && isChromeBrowser() && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm">
                      <p className="text-yellow-800 font-medium mb-1">
                        📌 Extension Not Detected
                      </p>
                      <p className="text-yellow-700 text-xs">
                        Make sure the LinkedIn Lead Checker extension is installed and enabled.
                      </p>
                    </div>
                  )}
                  
                  {!isChromeBrowser() && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
                      <p className="text-blue-800 font-medium mb-1">
                        💡 Use Chrome Browser
                      </p>
                      <p className="text-blue-700 text-xs">
                        The extension works on Chrome, Edge, and Chromium-based browsers.
                      </p>
                    </div>
                  )}
                </>
              )}
              
              {isChecking && (
                <div className="text-center py-2 text-gray-500 text-sm">
                  Checking for extension...
                </div>
              )}
              
              <button
                onClick={handleGoToDashboard}
                className="w-full px-8 py-4 text-blue-600 border-2 border-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
              >
                Go to Dashboard
              </button>
            </div>

            {/* Instructions Modal */}
            {showInstructions && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <div className="bg-white rounded-lg max-w-md w-full p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    How to Open the Extension
                  </h3>
                  
                  <div className="space-y-4 text-sm text-gray-700">
                    <div className="flex items-start">
                      <span className="font-bold text-blue-600 mr-3">1.</span>
                      <p>Click the <strong>Extensions icon</strong> (puzzle piece) in your browser toolbar</p>
                    </div>
                    
                    <div className="flex items-start">
                      <span className="font-bold text-blue-600 mr-3">2.</span>
                      <p>Find <strong>LinkedIn Lead Checker</strong> in the list</p>
                    </div>
                    
                    <div className="flex items-start">
                      <span className="font-bold text-blue-600 mr-3">3.</span>
                      <p>Click on it to open the extension</p>
                    </div>
                    
                    <div className="bg-blue-50 rounded-lg p-3 mt-4">
                      <p className="text-blue-800 text-xs">
                        💡 <strong>Tip:</strong> Pin the extension to your toolbar for quick access!
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-6 space-y-2">
                    <button
                      onClick={() => {
                        setShowInstructions(false);
                        window.close();
                      }}
                      className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                    >
                      Got it, Close Tab
                    </button>
                    
                    <button
                      onClick={() => setShowInstructions(false)}
                      className="w-full px-4 py-3 text-gray-600 hover:text-gray-800 font-medium transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Session ID (for debugging) */}
            {session_id && (
              <p className="text-xs text-gray-400 text-center mt-6">
                Session: {session_id.slice(0, 20)}...
              </p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

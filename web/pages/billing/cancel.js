import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { useChromeExtension, isChromeBrowser } from '../../lib/extension';
import Button from '../../components/Button';
import styles from '../../styles/Dashboard.module.css';

export default function BillingCancel() {
  const router = useRouter();
  const { isInstalled, isChecking, openExtension } = useChromeExtension();
  const [showInstructions, setShowInstructions] = useState(false);

  const handleBackToPricing = () => {
    router.push('/#pricing');
  };

  const handleContactSupport = () => {
    router.push('/support');
  };

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

  return (
    <>
      <Head>
        <title>Payment Cancelled - LinkedIn Lead Checker</title>
        <meta name="robots" content="noindex" />
      </Head>
      <div className={styles.container}>
        <div className="min-h-screen flex items-center justify-center py-12 px-4">
          <div className="max-w-lg w-full bg-white rounded-lg shadow-xl p-8">
            {/* Cancel Icon */}
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                <svg className="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Payment Cancelled
              </h1>
              <p className="text-gray-600">
                You have cancelled the payment process
              </p>
            </div>

            {/* Information */}
            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <p className="text-gray-700 text-center mb-4">
                No charges were made to your account. Your current plan remains unchanged.
              </p>
              
              <div className="border-t border-gray-200 pt-4">
                <p className="text-sm text-gray-600 text-center">
                  If you experienced any issues during checkout or have questions about our plans, please contact our support team.
                </p>
              </div>
            </div>

            {/* Why Upgrade Section */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">
                💡 Why upgrade?
              </h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Analyze more LinkedIn profiles per month</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Get AI-powered lead qualification</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Save hours of manual research</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Priority support and updates</span>
                </li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Button 
                variant="primary" 
                onClick={handleBackToPricing}
                className="w-full"
              >
                View Pricing Plans
              </Button>
              
              {!isChecking && (
                <>
                  <button
                    onClick={handleBackToExtension}
                    className="w-full px-8 py-4 text-gray-700 border-2 border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                  >
                    {isInstalled ? 'Back to Extension' : 'Open Extension'}
                  </button>
                  
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
                </>
              )}
              
              {isChecking && (
                <div className="text-center py-2 text-gray-500 text-sm">
                  Checking for extension...
                </div>
              )}
              
              <button
                onClick={handleContactSupport}
                className="w-full px-8 py-4 text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                Contact Support
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

            {/* Reassurance */}
            <div className="mt-6 text-center">
              <p className="text-xs text-gray-500">
                🔒 All payments are secure and processed by Stripe
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

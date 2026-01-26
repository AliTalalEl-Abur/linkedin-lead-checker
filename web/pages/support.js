import Head from 'next/head';
import Link from 'next/link';

export default function Support() {
  return (
    <>
      <Head>
        <title>Support & FAQ - LinkedIn Lead Checker</title>
        <meta name="description" content="Get help and find answers to common questions about LinkedIn Lead Checker" />
      </Head>

      <main className="bg-white min-h-screen">
        <div className="max-w-4xl mx-auto px-6 py-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Support & FAQ</h1>
          <p className="text-xl text-gray-600 mb-12">
            Find answers to common questions or contact our support team
          </p>

          {/* Contact Section */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 mb-12">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Need Help?</h2>
            <p className="text-gray-700 mb-4">
              Our support team is here to help. Contact us via email:
            </p>
            <a 
              href="mailto:support@linkedin-lead-checker.com"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              support@linkedin-lead-checker.com
            </a>
          </div>

          {/* FAQ Section */}
          <div className="space-y-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>

            {/* Getting Started */}
            <div className="border-b border-gray-200 pb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Getting Started</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">How do I install the extension?</h4>
                  <p className="text-gray-700">
                    Visit the Chrome Web Store, search for &quot;LinkedIn Lead Checker&quot;, and click &quot;Add to Chrome&quot;. Once installed, you&apos;ll see the extension icon in your browser toolbar.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Do I need an account?</h4>
                  <p className="text-gray-700">
                    Yes. A free account is required to use the extension. You can sign up directly from the extension popup - no credit card needed for the free preview.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">How do I analyze a LinkedIn profile?</h4>
                  <p className="text-gray-700">
                    Navigate to any LinkedIn profile page (linkedin.com/in/username), click the extension icon in your toolbar, log in (if not already), and click &quot;Analyze&quot;.
                  </p>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="border-b border-gray-200 pb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Features</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">What&apos;s included in the free preview?</h4>
                  <p className="text-gray-700">
                    The free preview shows basic profile information including name, job title, company, and headline. It&apos;s great for getting a quick overview before deciding to do a full analysis.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">What does the full AI analysis include?</h4>
                  <p className="text-gray-700">
                    Full AI analysis (subscription required) provides: lead scoring (0-100), priority recommendation (High/Medium/Low), personalized outreach strategy, deal size estimation, buying signal detection, and detailed insights.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">How accurate is the AI analysis?</h4>
                  <p className="text-gray-700">
                    Our AI is trained on thousands of successful sales interactions and provides guidance based on publicly available profile data. However, results should be used as a starting point for your own research and judgment.
                  </p>
                </div>
              </div>
            </div>

            {/* Billing */}
            <div className="border-b border-gray-200 pb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Billing & Subscriptions</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">What are the subscription plans?</h4>
                  <ul className="text-gray-700 list-disc pl-6 space-y-1">
                    <li>Starter: $9/month - 40 AI analyses</li>
                    <li>Pro: $19/month - 150 AI analyses</li>
                    <li>Team: $49/month - 500 AI analyses</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">When do my analysis credits reset?</h4>
                  <p className="text-gray-700">
                    Credits reset on the first day of each billing cycle (monthly from your subscription start date). Unused credits do not roll over.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Can I cancel anytime?</h4>
                  <p className="text-gray-700">
                    Yes! You can cancel your subscription anytime from your dashboard. You&apos;ll continue to have access until the end of your current billing period.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Do you offer refunds?</h4>
                  <p className="text-gray-700">
                    Yes. Refunds are available within 7 days of initial purchase if you&apos;ve used fewer than 5 AI analyses. Contact support@linkedin-lead-checker.com for refund requests.
                  </p>
                </div>
              </div>
            </div>

            {/* Privacy & Security */}
            <div className="border-b border-gray-200 pb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Privacy & Security</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">What data do you collect?</h4>
                  <p className="text-gray-700">
                    We only collect data when you click &quot;Analyze&quot; on a LinkedIn profile. This includes publicly visible profile information (name, headline, job titles, about section). See our <Link href="/privacy" className="text-blue-600 hover:underline">Privacy Policy</Link> for full details.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Do you sell my data?</h4>
                  <p className="text-gray-700">
                    No. We never sell your data to third parties. Your profile analyses are private and only visible to you.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Is my payment information secure?</h4>
                  <p className="text-gray-700">
                    Yes. All payments are processed through Stripe, an industry-leading payment processor. We never store your credit card details on our servers.
                  </p>
                </div>
              </div>
            </div>

            {/* Technical Issues */}
            <div className="pb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Technical Issues</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">The extension isn&apos;t working. What should I do?</h4>
                  <ol className="text-gray-700 list-decimal pl-6 space-y-2">
                    <li>Make sure you&apos;re on a LinkedIn profile page (linkedin.com/in/username)</li>
                    <li>Try refreshing the page</li>
                    <li>Log out and log back in to the extension</li>
                    <li>Disable and re-enable the extension in Chrome settings</li>
                    <li>If issues persist, contact support with details about the error</li>
                  </ol>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">I&apos;m getting an error message</h4>
                  <p className="text-gray-700">
                    Please take a screenshot of the error and email it to support@linkedin-lead-checker.com. Include details about what you were doing when the error occurred.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Can I use this on mobile?</h4>
                  <p className="text-gray-700">
                    Currently, LinkedIn Lead Checker is only available as a Chrome extension for desktop browsers. Mobile support may be added in the future.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Contact CTA */}
          <div className="mt-12 text-center bg-gray-50 rounded-lg p-8">
            <h3 className="text-2xl font-semibold text-gray-900 mb-4">
              Didn&apos;t find what you were looking for?
            </h3>
            <p className="text-gray-600 mb-6">
              Our support team is happy to help with any questions
            </p>
            <a 
              href="mailto:support@linkedin-lead-checker.com"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              Contact Support
            </a>
          </div>
        </div>
      </main>
    </>
  );
}

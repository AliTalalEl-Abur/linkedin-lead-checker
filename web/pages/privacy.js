import Head from 'next/head';

export default function PrivacyPolicy() {
  return (
    <>
      <Head>
        <title>Privacy Policy - LinkedIn Lead Checker</title>
        <meta name="description" content="Privacy Policy for LinkedIn Lead Checker Chrome Extension" />
        <meta name="robots" content="index, follow" />
      </Head>

      <main className="bg-white min-h-screen">
        <div className="max-w-4xl mx-auto px-6 py-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
          <p className="text-gray-600 mb-8">Last Updated: January 24, 2026</p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Introduction</h2>
              <p className="text-gray-700 leading-relaxed">
                LinkedIn Lead Checker (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) provides a Chrome extension that helps users analyze LinkedIn profiles for lead qualification purposes. We are committed to protecting your privacy and being transparent about how we collect and use data.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">What Data We Collect</h2>
              
              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">1. Account Information</h3>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li><strong>Email address</strong>: Used for account creation and authentication</li>
                <li><strong>Password</strong>: Stored as a secure hash, never in plain text</li>
                <li><strong>Subscription details</strong>: Plan type, payment status (processed by Stripe)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">2. Profile Analysis Data</h3>
              <p className="text-gray-700 mb-3">When you click &quot;Analyze&quot; on a LinkedIn profile, we collect:</p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Profile name (public display name from LinkedIn)</li>
                <li>Headline (job title/headline from profile)</li>
                <li>About section (public bio/summary text)</li>
                <li>Experience titles (job titles from work history)</li>
                <li>Profile URL (LinkedIn profile link)</li>
              </ul>
              <p className="text-gray-700 mt-3 font-semibold">
                Important: This data is ONLY collected when you explicitly click the &quot;Analyze&quot; button. We do NOT automatically collect data in the background.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">3. Usage Data</h3>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Analysis count (for subscription limits)</li>
                <li>Analysis timestamps</li>
                <li>API requests (server logs for debugging and security)</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">How We Use Your Data</h2>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Generate AI-powered lead qualification reports</li>
                <li>Provide scoring, recommendations, and outreach strategies</li>
                <li>Authenticate your identity</li>
                <li>Enforce subscription limits</li>
                <li>Process payments (via Stripe)</li>
                <li>Send service-related communications</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Sharing</h2>
              
              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">We DO NOT:</h3>
              <ul className="list-none pl-0 text-gray-700 space-y-2">
                <li>❌ Sell your data to third parties</li>
                <li>❌ Share profile analysis data with anyone</li>
                <li>❌ Use your data for advertising</li>
                <li>❌ Share your email with marketers</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">We DO share data with:</h3>
              <ul className="list-none pl-0 text-gray-700 space-y-2">
                <li>✅ <strong>Stripe</strong>: Payment processing (subject to Stripe&apos;s privacy policy)</li>
                <li>✅ <strong>OpenAI</strong>: Profile data sent for AI analysis (subject to OpenAI&apos;s data policies)</li>
                <li>✅ <strong>Law enforcement</strong>: Only if legally required by valid court order</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Storage & Security</h2>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>All data transmitted over HTTPS encryption</li>
                <li>Passwords hashed with industry-standard bcrypt</li>
                <li>Authentication tokens stored locally in Chrome&apos;s secure storage</li>
                <li>Server-side data encrypted at rest</li>
                <li>Regular security audits and updates</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Your Rights</h2>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li><strong>Access your data</strong>: View all your analysis history in the dashboard</li>
                <li><strong>Export your data</strong>: Request a copy of all your data (JSON format)</li>
                <li><strong>Delete your data</strong>: Delete your account and all associated data anytime</li>
                <li><strong>Opt-out of emails</strong>: Unsubscribe from marketing emails</li>
              </ul>
              <p className="text-gray-700 mt-4">
                To exercise these rights, email us at: <a href="mailto:privacy@linkedin-lead-checker.com" className="text-blue-600 hover:underline">privacy@linkedin-lead-checker.com</a>
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">How the Extension Works</h2>
              <p className="text-gray-700 mb-3"><strong>User-Initiated Only</strong></p>
              <p className="text-gray-700 mb-3">The extension ONLY collects data when you:</p>
              <ol className="list-decimal pl-6 text-gray-700 space-y-2">
                <li>Visit a LinkedIn profile page</li>
                <li>Click the extension icon</li>
                <li>Click the &quot;Analyze&quot; button</li>
              </ol>
              <p className="text-gray-700 mt-4 font-semibold">No Background Activity</p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>No automatic scraping</li>
                <li>No background data collection</li>
                <li>No tracking of your browsing activity</li>
                <li>Extension only activates on LinkedIn profile pages</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Contact Us</h2>
              <p className="text-gray-700">
                Privacy Questions: <a href="mailto:privacy@linkedin-lead-checker.com" className="text-blue-600 hover:underline">privacy@linkedin-lead-checker.com</a>
              </p>
              <p className="text-gray-700">
                General Support: <a href="mailto:support@linkedin-lead-checker.com" className="text-blue-600 hover:underline">support@linkedin-lead-checker.com</a>
              </p>
              <p className="text-gray-700">
                Website: <a href="https://linkedin-lead-checker.vercel.app" className="text-blue-600 hover:underline">linkedin-lead-checker.vercel.app</a>
              </p>
            </section>

            <div className="bg-blue-50 border-l-4 border-blue-600 p-6 mt-8">
              <p className="text-gray-800 font-semibold">
                By using LinkedIn Lead Checker, you agree to this Privacy Policy.
              </p>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

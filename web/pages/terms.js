import Head from 'next/head';
import Link from 'next/link';

export default function TermsOfService() {
  return (
    <>
      <Head>
        <title>Terms of Service - LinkedIn Lead Checker</title>
        <meta name="description" content="Terms of Service for LinkedIn Lead Checker" />
        <meta name="robots" content="index, follow" />
      </Head>

      <main className="bg-white min-h-screen">
        <div className="max-w-4xl mx-auto px-6 py-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
          <p className="text-gray-600 mb-8">Last Updated: January 24, 2026</p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700 leading-relaxed">
                By accessing or using LinkedIn Lead Checker (&quot;the Service&quot;), you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                LinkedIn Lead Checker is a Chrome extension that helps users analyze LinkedIn profiles for lead qualification purposes. The Service includes:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Free preview of basic profile information</li>
                <li>AI-powered lead analysis (subscription required)</li>
                <li>Lead scoring and recommendations</li>
                <li>Analysis history and dashboard</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Responsibilities</h2>
              <p className="text-gray-700 mb-3">You agree to:</p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Provide accurate account information</li>
                <li>Maintain the security of your account credentials</li>
                <li>Use the Service in compliance with LinkedIn&apos;s Terms of Service</li>
                <li>Not use the Service for spam, harassment, or illegal activities</li>
                <li>Not attempt to reverse engineer or scrape the Service</li>
                <li>Not share your account with others</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Subscription and Payment</h2>
              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Free Preview</h3>
              <p className="text-gray-700 mb-3">
                Basic profile preview is free with no credit card required. Limited functionality applies.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Paid Subscriptions</h3>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Starter: $9/month - 40 AI analyses per month</li>
                <li>Pro: $19/month - 150 AI analyses per month</li>
                <li>Business: $49/month - 500 AI analyses per month</li>
              </ul>
              <p className="text-gray-700 mt-3">
                Subscriptions automatically renew monthly unless canceled. You can cancel anytime from your dashboard.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Refunds</h3>
              <p className="text-gray-700">
                Refunds are available within 7 days of initial purchase if you have used fewer than 5 AI analyses. Contact support@linkedin-lead-checker.com for refund requests.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Usage Limits</h2>
              <p className="text-gray-700 mb-3">
                Each subscription plan includes a monthly analysis limit. Limits reset on the first day of each billing cycle. Unused analyses do not roll over to the next month.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Data and Privacy</h2>
              <p className="text-gray-700">
                Your use of the Service is governed by our <Link href="/privacy" className="text-blue-600 hover:underline">Privacy Policy</Link>. By using the Service, you consent to our collection and use of data as described in the Privacy Policy.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Acceptable Use</h2>
              <p className="text-gray-700 mb-3">You may NOT use the Service to:</p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Violate LinkedIn&apos;s Terms of Service</li>
                <li>Send spam or unsolicited messages</li>
                <li>Harass or stalk individuals</li>
                <li>Collect data for resale or redistribution</li>
                <li>Automate profile analysis beyond normal human usage</li>
                <li>Access the Service through unauthorized means</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Intellectual Property</h2>
              <p className="text-gray-700 mb-3">
                The Service, including all content, features, and functionality, is owned by LinkedIn Lead Checker and is protected by copyright, trademark, and other intellectual property laws.
              </p>
              <p className="text-gray-700">
                You may not copy, modify, distribute, or create derivative works based on the Service without our express written permission.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Disclaimers</h2>
              <p className="text-gray-700 mb-3 font-semibold uppercase">
                THE SERVICE IS PROVIDED &quot;AS IS&quot; WITHOUT WARRANTIES OF ANY KIND.
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>We do not guarantee the accuracy of AI-generated analyses</li>
                <li>We do not guarantee uninterrupted or error-free service</li>
                <li>LinkedIn profile data may be incomplete or outdated</li>
                <li>Results are for informational purposes only</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Limitation of Liability</h2>
              <p className="text-gray-700">
                LinkedIn Lead Checker shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of the Service. Our total liability shall not exceed the amount you paid for the Service in the past 12 months.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Termination</h2>
              <p className="text-gray-700 mb-3">
                We reserve the right to suspend or terminate your account if you violate these Terms of Service. You may delete your account at any time from your dashboard.
              </p>
              <p className="text-gray-700">
                Upon termination, your right to use the Service will immediately cease, and all your data will be deleted within 30 days.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Changes to Terms</h2>
              <p className="text-gray-700">
                We may update these Terms of Service from time to time. We will notify you of significant changes by email or by posting a notice in the Service. Your continued use of the Service after changes constitutes acceptance of the new terms.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Governing Law</h2>
              <p className="text-gray-700">
                These Terms of Service shall be governed by and construed in accordance with the laws of the jurisdiction in which LinkedIn Lead Checker operates, without regard to conflict of law principles.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">14. Contact Information</h2>
              <p className="text-gray-700">
                For questions about these Terms of Service, contact us at:
              </p>
              <p className="text-gray-700 mt-2">
                Email: <a href="mailto:support@linkedin-lead-checker.com" className="text-blue-600 hover:underline">support@linkedin-lead-checker.com</a>
              </p>
              <p className="text-gray-700">
                Website: <a href="https://linkedin-lead-checker.vercel.app" className="text-blue-600 hover:underline">linkedin-lead-checker.vercel.app</a>
              </p>
            </section>

            <div className="bg-gray-100 border-l-4 border-gray-600 p-6 mt-8">
              <p className="text-gray-800">
                <strong>By using LinkedIn Lead Checker, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.</strong>
              </p>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

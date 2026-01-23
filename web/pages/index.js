import { useState } from 'react';
import Head from 'next/head';
import Button from '../components/Button';
import Section from '../components/Section';
import PricingCard from '../components/PricingCard';

export default function Home() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleEarlyAccess = (e) => {
    e.preventDefault();
    // Simple validation - no backend required
    if (email && email.includes('@')) {
      setSubmitted(true);
      // In production, this would send to your email collection service
      console.log('Early access email:', email);
    }
  };

  return (
    <>
      <Head>
        <title>LinkedIn Lead Checker - Instantly Know If a Profile Is Worth Contacting</title>
        <meta name="description" content="A lightweight Chrome extension that gives you an instant lead fit preview before you waste time writing messages." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="bg-white">
        {/* HERO SECTION */}
        <Section className="pt-20 md:pt-32 pb-16 md:pb-24" background="gray">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Instantly Know If a LinkedIn Profile<br />Is Worth Contacting
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto">
              A lightweight Chrome extension that gives you an instant lead fit preview before you waste time writing messages.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button variant="primary" onClick={() => window.open('https://chrome.google.com/webstore', '_blank')}>
                Install Chrome Extension (Free Preview)
              </Button>
              <Button variant="secondary" onClick={() => document.getElementById('how-to-try').scrollIntoView({ behavior: 'smooth' })}>
                See how it works
              </Button>
            </div>
            <p className="text-sm text-gray-500 mt-3">Works instantly on LinkedIn profiles. No credit card required.</p>

            {/* Visual placeholder for extension preview */}
            <div className="mt-16 bg-white rounded-lg shadow-2xl p-8 max-w-4xl mx-auto border border-gray-200">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-12 text-center">
                <svg className="w-24 h-24 mx-auto text-blue-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-gray-600 text-lg">Chrome Extension Preview</p>
              </div>
            </div>
          </div>
        </Section>

        {/* QUICK TRY SECTION */}
        <Section background="white" id="how-to-try">
          <div className="max-w-3xl mx-auto text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">How to try it in under 30 seconds</h3>
            <ul className="text-gray-700 space-y-2 text-base list-disc list-inside text-left inline-block">
              <li>Install the Chrome extension</li>
              <li>Log in (free)</li>
              <li>Open any LinkedIn profile</li>
              <li>Click &quot;Analyze&quot;</li>
            </ul>
          </div>
        </Section>

        {/* PROBLEM SECTION */}
        <Section background="white">
          <div className="text-center mb-12">
            <h2 className="section-title">
              Most LinkedIn Outreach Fails for One Reason
            </h2>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ),
                text: 'You contact people who will never reply'
              },
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                text: 'You waste time checking profiles manually'
              },
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                text: "You don't know if someone fits your ICP"
              },
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                text: 'AI tools are expensive or overkill'
              }
            ].map((problem, index) => (
              <div key={index} className="text-center p-6 rounded-lg bg-red-50 border border-red-100">
                <div className="text-red-600 mb-4 flex justify-center">
                  {problem.icon}
                </div>
                <p className="text-gray-800 font-medium">{problem.text}</p>
              </div>
            ))}
          </div>
        </Section>

        {/* SOLUTION SECTION */}
        <Section background="gray">
          <div className="text-center mb-12">
            <h2 className="section-title">
              How LinkedIn Lead Checker Helps
            </h2>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                  </svg>
                ),
                title: 'One click from any LinkedIn profile',
                description: 'No complex setup or configuration needed'
              },
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                ),
                title: 'Instant lead fit preview',
                description: 'Get results in seconds, not minutes'
              },
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                ),
                title: 'Clear signals: fit, risk, priority',
                description: 'Simple scores you can act on immediately'
              },
              {
                icon: (
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                ),
                title: 'Built for sales, recruiters & founders',
                description: 'Designed for B2B outreach professionals'
              }
            ].map((solution, index) => (
              <div key={index} className="text-center p-6 rounded-lg bg-white border-2 border-blue-100 hover:border-blue-500 transition-all duration-200">
                <div className="text-blue-600 mb-4 flex justify-center">
                  {solution.icon}
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{solution.title}</h3>
                <p className="text-gray-600 text-sm">{solution.description}</p>
              </div>
            ))}
          </div>
        </Section>

        {/* HOW IT WORKS SECTION */}
        <Section background="white">
          <div className="text-center mb-12">
            <h2 className="section-title">
              How It Works
            </h2>
            <p className="section-subtitle">
              Simple. Fast. No complexity.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-12">
            {[
              {
                step: '1',
                title: 'Open a LinkedIn profile',
                description: 'Navigate to any LinkedIn profile you want to evaluate'
              },
              {
                step: '2',
                title: 'Click the extension',
                description: 'One click on the Chrome extension icon in your browser'
              },
              {
                step: '3',
                title: 'Get an instant lead assessment',
                description: 'See fit score, key signals, and whether to reach out'
              }
            ].map((step, index) => (
              <div key={index} className="text-center relative">
                <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {step.step}
                </div>
                {index < 2 && (
                  <div className="hidden md:block absolute top-8 left-[60%] w-[80%] border-t-2 border-dashed border-blue-300"></div>
                )}
                <h3 className="text-xl font-bold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>

          <div className="bg-blue-50 border-l-4 border-blue-600 p-6 max-w-2xl mx-auto rounded-r-lg">
            <p className="text-gray-800 text-center font-medium">
              No scraping. No spam. No automation. Just decision support.
            </p>
          </div>
        </Section>

        {/* SOCIAL PROOF SECTION */}
        <Section background="gray">
          <div className="text-center max-w-3xl mx-auto">
            <div className="mb-8">
              <svg className="w-16 h-16 text-blue-600 mx-auto" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
              </svg>
            </div>
            <p className="text-2xl text-gray-800 font-medium mb-6 italic">
              &ldquo;Early users use LinkedIn Lead Checker to quickly decide who is worth contacting — and who isn&apos;t.&rdquo;
            </p>
            <p className="text-gray-600">
              Join sales professionals, recruiters, and founders who are saving time on LinkedIn outreach.
            </p>
          </div>
        </Section>

        {/* PRICING SECTION */}
        <Section background="white">
          <div className="text-center mb-12">
            <h2 className="section-title">
              Pricing (Launching Soon)
            </h2>
            <p className="section-subtitle">
              Get started with our free preview. Full AI coming soon.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <PricingCard
              title="Free Preview"
              description="Try before you commit"
              features={[
                'Limited lifetime previews',
                'No credit card required',
                'Basic lead fit signals',
                'One-click analysis',
                'Perfect for testing the tool'
              ]}
              cta="Install Extension"
            />
            
            <PricingCard
              title="Pro"
              description="Coming Soon"
              badge="Most Popular"
              features={[
                'Full AI-powered analysis',
                'Higher usage limits',
                'Built for daily outreach',
                'Priority support',
                'Advanced lead scoring'
              ]}
              cta="Join Waitlist"
            />
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 text-lg">
              Pricing will be fair, simple and transparent.
            </p>
          </div>
        </Section>

        {/* FINAL CTA SECTION */}
        <Section background="gray" id="early-access">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="section-title">
              Stop Guessing on LinkedIn
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Join the early access list and be the first to know when full AI analysis launches.
            </p>
            
            {!submitted ? (
              <form onSubmit={handleEarlyAccess} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="flex-1 px-6 py-4 rounded-lg border-2 border-gray-300 focus:border-blue-600 focus:outline-none text-lg"
                  required
                />
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-4 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg whitespace-nowrap"
                >
                  Join Waitlist
                </button>
              </form>
            ) : (
              <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6 max-w-md mx-auto">
                <svg className="w-12 h-12 text-green-500 mx-auto mb-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <p className="text-green-800 font-semibold text-lg">Thank you for joining!</p>
                <p className="text-green-700 mt-2">We&apos;ll notify you when we launch.</p>
              </div>
            )}
          </div>
        </Section>

        {/* FOOTER */}
        <footer className="bg-gray-900 text-gray-300 py-12">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="text-center mb-6">
              <h3 className="text-white text-xl font-bold mb-2">LinkedIn Lead Checker</h3>
              <p className="text-gray-400 text-sm max-w-md mx-auto">
                Built by an independent developer. Not affiliated with LinkedIn.
              </p>
              <p className="text-gray-500 text-xs mt-3">This is a working preview version. Full AI analysis is coming soon.</p>
            </div>
            
            <div className="flex justify-center gap-8 text-sm">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
            
            <div className="text-center mt-8 text-gray-500 text-sm">
              © {new Date().getFullYear()} LinkedIn Lead Checker. All rights reserved.
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}

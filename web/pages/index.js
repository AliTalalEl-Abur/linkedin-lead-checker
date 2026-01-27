import { useState, useEffect } from 'react';
import Head from 'next/head';
import Button from '../components/Button';
import Section from '../components/Section';
import PricingCard from '../components/PricingCard';
import { getStoredToken, authenticatedFetch } from '../lib/api';
import { trackEvent } from '../lib/tracking';

// SEO Metadata
const META = {
  title: 'LinkedIn Lead Checker - AI-Powered Lead Qualification',
  description: 'Qualify LinkedIn leads in seconds with AI analysis. Stop wasting time on bad-fit prospects. Get instant scoring, priority recommendations, and personalized outreach strategies.',
  url: 'https://linkedin-lead-checker.vercel.app',
  ogImage: 'https://linkedin-lead-checker.vercel.app/og-image.jpg'
};

export default function Home() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [softLaunchMode, setSoftLaunchMode] = useState(false);
  const [userState, setUserState] = useState({
    loading: true,
    isAuthenticated: false,
    hasSubscription: false,
    plan: null
  });

  // Check authentication status on mount (client-side only)
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = getStoredToken();
      
      if (!token) {
        setUserState({ loading: false, isAuthenticated: false, hasSubscription: false, plan: null });
        return;
      }

      try {
        const data = await authenticatedFetch('/user', { method: 'GET' });
        const hasActivePlan = data.plan && ['starter', 'pro', 'team'].includes(data.plan);
        
        setUserState({
          loading: false,
          isAuthenticated: true,
          hasSubscription: hasActivePlan,
          plan: data.plan
        });
      } catch (error) {
        console.error('Auth check failed:', error);
        setUserState({ loading: false, isAuthenticated: false, hasSubscription: false, plan: null });
      }
    };

    const checkSoftLaunch = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/health`);
        const data = await response.json();
        setSoftLaunchMode(data.soft_launch_mode || false);
      } catch (error) {
        // Silent fail - soft launch check is optional
      }
    };

    checkAuthStatus();
    checkSoftLaunch();
  }, []);

  const handleEarlyAccess = (e) => {
    e.preventDefault();
    // Simple validation - no backend required
    if (email && email.includes('@')) {
      trackEvent('waitlist_join', 'landing');
      setSubmitted(true);
    }
  };

  // Dynamic CTA logic
  const getPrimaryCTA = () => {
    // Always point to Chrome Web Store for installation
    return {
      text: 'Install Chrome Extension',
      onClick: () => {
        trackEvent('install_extension_click', 'landing');
        window.open('https://chrome.google.com/webstore', '_blank');
      }
    };
  };

  // Get dynamic subtitle text
  const getSubtitleText = () => {
    if (!userState.isAuthenticated) {
      return 'Free preview instantly. Full AI analysis requires subscription.';
    }
    if (userState.hasSubscription) {
      return `Active ${userState.plan} plan - Full AI analysis enabled`;
    }
    return 'Preview works instantly. Full AI requires upgrade.';
  };

  const primaryCTA = getPrimaryCTA();

  // Handle checkout by calling backend API
  const handleCheckout = async (planName) => {
    const plan = planName.toLowerCase();
    
    try {
      // Get return URL for after payment
      const returnUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/billing-return.html?session_id={CHECKOUT_SESSION_ID}`;
      
      // Call backend to create Stripe checkout session
      const response = await authenticatedFetch('/billing/checkout', {
        method: 'POST',
        body: JSON.stringify({ 
          return_url: returnUrl,
          plan: plan
        })
      });

      // Redirect to Stripe checkout
      if (response.url) {
        window.location.href = response.url;
      } else {
        console.error('No checkout URL received');
        alert('Error creating checkout session. Please try again.');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      
      // If authentication error, redirect to login
      if (error.message.includes('Session expired') || error.message.includes('Not authenticated')) {
        window.location.href = '/login';
      } else {
        alert('Error: ' + error.message);
      }
    }
  };

  // Dynamic CTA for pricing cards
  const getPricingCTA = (planName) => {
    if (userState.loading) {
      return {
        text: 'Get Started',
        onClick: () => {}
      };
    }

    // Not authenticated - redirect to login/signup
    if (!userState.isAuthenticated) {
      return {
        text: 'Get Started',
        onClick: () => window.location.href = '/login'
      };
    }

    // Authenticated but no subscription - go to checkout
    if (!userState.hasSubscription) {
      return {
        text: 'Subscribe Now',
        onClick: () => handleCheckout(planName)
      };
    }

    // Already subscribed to this plan
    if (userState.plan === planName.toLowerCase()) {
      return {
        text: 'Current Plan',
        onClick: () => window.location.href = '/dashboard'
      };
    }

    // Subscribed to different plan - upgrade/downgrade
    return {
      text: 'Switch Plan',
      onClick: () => handleCheckout(planName)
    };
  };

  return (
    <>
      <Head>
        <title>{META.title}</title>
        <meta name="description" content={META.description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        
        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content={META.url} />
        <meta property="og:title" content={META.title} />
        <meta property="og:description" content={META.description} />
        <meta property="og:image" content={META.ogImage} />
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:url" content={META.url} />
        <meta name="twitter:title" content={META.title} />
        <meta name="twitter:description" content={META.description} />
        <meta name="twitter:image" content={META.ogImage} />
        
        {/* Additional SEO */}
        <meta name="keywords" content="LinkedIn, lead qualification, AI, B2B sales, lead scoring, sales automation" />
        <meta name="author" content="LinkedIn Lead Checker" />
        <link rel="canonical" href={META.url} />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="bg-white">
        {/* EARLY ACCESS BADGE */}
        {softLaunchMode && (
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '20px',
            fontWeight: 'bold',
            fontSize: '14px',
            zIndex: 1000,
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            🚀 Early Access
          </div>
        )}

        {/* HERO SECTION */}
        <Section className="pt-20 md:pt-32 pb-16 md:pb-24" background="gray">
          <div className="text-center">{softLaunchMode && (
              <div style={{
                background: 'rgba(102, 126, 234, 0.1)',
                border: '1px solid rgba(102, 126, 234, 0.3)',
                borderRadius: '8px',
                padding: '12px 20px',
                marginBottom: '24px',
                display: 'inline-block'
              }}>
                <span style={{ fontSize: '16px' }}>
                  ✨ You're among the first! Help us improve with your feedback.
                </span>
              </div>
            )}
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Instantly Know If a LinkedIn Profile<br />Is Worth Contacting
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto">
              A lightweight Chrome extension that gives you an instant preview. Full AI-powered analysis available with subscription.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                variant="primary" 
                onClick={primaryCTA.onClick}
                disabled={userState.loading}
              >
                {primaryCTA.text}
              </Button>
              <Button variant="secondary" onClick={() => {
                const section = document.getElementById('how-it-works');
                if (section) section.scrollIntoView({ behavior: 'smooth' });
              }}>
                How it works
              </Button>
            </div>
            <p className="text-sm text-gray-500 mt-3">
              {userState.loading ? 'Loading...' : getSubtitleText()}
            </p>

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

        {/* HOW IT WORKS SECTION */}
        <Section background="white" id="how-it-works">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-12 text-center">
              How it works
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8 mb-12">
              <div className="bg-blue-50 p-8 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  🆓 Free Preview (Always Available)
                </h3>
                <ul className="text-gray-700 space-y-3">
                  <li>✓ Install Chrome extension</li>
                  <li>✓ Visit any LinkedIn profile</li>
                  <li>✓ Get instant basic fit indicators</li>
                  <li>✓ See job title, company, location</li>
                </ul>
              </div>
              
              <div className="bg-gradient-to-br from-blue-100 to-purple-100 p-8 rounded-lg border-2 border-blue-300">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  ⚡ Full AI Analysis (Subscription)
                </h3>
                <ul className="text-gray-700 space-y-3">
                  <li>✓ AI-powered lead scoring (0-100)</li>
                  <li>✓ Priority recommendations</li>
                  <li>✓ Personalized outreach strategy</li>
                  <li>✓ Deal size estimation</li>
                  <li>✓ Buying signal detection</li>
                </ul>
              </div>
            </div>
            
            <div className="text-center">
              <p className="text-lg text-gray-600 mb-6">
                Start with the free preview. Upgrade when you&apos;re ready for AI-powered insights.
              </p>
              <Button 
                variant="primary" 
                onClick={() => {
                  trackEvent('install_extension_click', 'how-it-works');
                  window.open('https://chrome.google.com/webstore', '_blank');
                }}
              >
                Get Started Free
              </Button>
            </div>
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
              Simple, Transparent Pricing
            </h2>
            <p className="section-subtitle">
              Choose the plan that fits your outreach needs
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <PricingCard
              title="Starter"
              price="9"
              period="month"
              description="Perfect for solo founders & light outreach"
              features={[
                'Up to 40 AI-powered lead analyses',
                'Perfect for solo founders & light outreach',
                'No credit card required to try preview',
                'LinkedIn profile analysis',
                'Lead fit scoring'
              ]}
              cta={getPricingCTA('starter').text}
              ctaOnClick={getPricingCTA('starter').onClick}
            />
            
            <PricingCard
              title="Pro"
              price="19"
              period="month"
              description="Built for daily LinkedIn outreach"
              badge="Most Popular"
              featured={true}
              features={[
                'Up to 150 AI-powered lead analyses',
                'Built for daily LinkedIn outreach',
                'Priority access to new features',
                'Advanced lead scoring',
                'Priority support'
              ]}
              cta={getPricingCTA('pro').text}
              ctaOnClick={getPricingCTA('pro').onClick}
            />
            
            <PricingCard
              title="Team"
              price="49"
              period="month"
              description="Ideal for teams & agencies"
              features={[
                'Up to 500 AI-powered lead analyses',
                'Ideal for teams & agencies',
                'Shared usage across members',
                'Dedicated support',
                'Custom integrations'
              ]}
              cta={getPricingCTA('team').text}
              ctaOnClick={getPricingCTA('team').onClick}
            />
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 text-base">
              Fair usage limits apply. No rollovers. Cancel anytime.
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

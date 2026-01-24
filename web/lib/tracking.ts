/**
 * Privacy-respecting event tracking
 * No cookies, no persistent IDs, just intent signals
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function trackEvent(
  event: 'install_extension_click' | 'waitlist_join',
  page: string = 'landing'
) {
  try {
    // Get referrer if available (non-invasive)
    const referrer = typeof document !== 'undefined' ? document.referrer : null;
    
    // Fire-and-forget tracking (don't block UI)
    fetch(`${API_URL}/events/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event,
        page,
        referrer: referrer || undefined
      }),
      // Don't wait for response
      keepalive: true
    }).catch(() => {
      // Silently fail - tracking should never break UX
    });
  } catch (error) {
    // Silently fail - tracking should never break UX
  }
}

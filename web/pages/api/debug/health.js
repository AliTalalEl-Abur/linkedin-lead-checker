const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://linkedin-lead-checker-api.onrender.com';

export default async function handler(req, res) {
  try {
    const response = await fetch(`${API_URL}/health`);
    const text = await response.text();
    res.status(response.status);
    res.setHeader('Content-Type', response.headers.get('content-type') || 'application/json');
    return res.send(text);
  } catch (error) {
    return res.status(502).json({
      detail: 'Health proxy failed',
      error: String(error?.message || error),
      apiUrl: API_URL,
    });
  }
}

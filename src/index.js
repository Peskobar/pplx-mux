/**
 * Proxy Cloudflare Worker dla Perplexity MUX
 * Rotacja dwóch kluczy PPLX_KEY_A i PPLX_KEY_B
 */
export default {
  async fetch(request, env) {
    if (request.method !== 'POST' || !new URL(request.url).pathname.startsWith('/chat/completions')) {
      return new Response('Not Found', { status: 404 })
    }
    const { PPLX_KEY_A, PPLX_KEY_B, DEFAULT_MODEL } = env
    const payload = await request.json()
    payload.model = payload.model || DEFAULT_MODEL
    const keys = [PPLX_KEY_A, PPLX_KEY_B].filter(k => k)
    if (keys.length === 0) {
      return new Response('Brak kluczy API', { status: 500 })
    }
    const key = keys[Math.floor(Math.random() * keys.length)]
    const res = await fetch('https://api.perplexity.ai/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    const text = await res.text()
    return new Response(text, {
      status: res.status,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

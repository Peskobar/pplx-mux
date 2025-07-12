/**
 * Proxy Cloudflare Worker dla API Perplexity
 * Losowa rotacja kluczy PPLX_KEY_A i PPLX_KEY_B
 */
export default {
  async fetch(zadanie, srodowisko) {
    const url = new URL(zadanie.url)
    if (zadanie.method !== 'POST' || url.pathname !== '/chat/completions') {
      return new Response('Nie znaleziono', { status: 404 })
    }
    const { PPLX_KEY_A, PPLX_KEY_B, DEFAULT_MODEL } = srodowisko
    const dane = await zadanie.json()
    if (!dane.model) {
      dane.model = DEFAULT_MODEL
    }
    const klucze = [PPLX_KEY_A, PPLX_KEY_B].filter(k => k)
    if (klucze.length === 0) {
      return new Response('Brak kluczy API', { status: 500 })
    }
    const klucz = klucze[Math.floor(Math.random() * klucze.length)]
    const odpowiedz = await fetch('https://api.perplexity.ai/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${klucz}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dane)
    })
    const tekst = await odpowiedz.text()
    return new Response(tekst, {
      status: odpowiedz.status,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

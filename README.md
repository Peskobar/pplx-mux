pplx-mux

Opis projektu

pplx-mux to lekki proxy dla API Perplexity PRO, wdrożony jako Cloudflare Worker. Umożliwia rotację dwóch kluczy API (PPLX_KEY_A i PPLX_KEY_B) oraz obsługę modeli (domyślnie sonar-pro), zapewniając równomierne rozłożenie zapytań i automatyczną zmianę kluczy w trybie round-robin, failover lub dual.

Funkcjonalności

POST /chat/completions – przekazuje zapytania do Perplexity AI z rotacją kluczy.

GET /health – sprawdza status proxy, zwraca JSON { status: "ok", mode: "<aktualny tryb>" }.


Struktura projektu

├── src/
│   └── index.js            # Kod Cloudflare Worker
├── mux/
│   ├── pplx_mux.py         # Proxy FastAPI (opcjonalne uruchomienie lokalne)
│   └── Dockerfile          # Multi-stage build dla kontenera Docker
├── .github/
│   └── workflows/
│       └── deploy.yml      # Workflow GitHub Actions do wdrożenia Workers
├── wrangler.toml           # Konfiguracja Cloudflare Worker
├── docker-compose.yml      # Definicja usługi do lokalnego uruchomienia
├── .env.template           # Szablon zmiennych środowiskowych
├── tests/                  # Testy jednostkowe (pytest)
├── README.md               # Dokumentacja projektu
└── requirements.txt        # Zależności Pythona (FastAPI)

Instalacja i uruchomienie lokalne

1. Skopiuj plik .env.template do .env i uzupełnij wartości:

PPLX_KEY_A=<twój klucz>
PPLX_KEY_B=<twój klucz>
MODE=round
DEFAULT_MODEL=sonar-pro
CF_API_TOKEN=<token Cloudflare>


2. Uruchom kontener lokalnie:

docker-compose up -d --build


3. Sprawdź health:

curl http://localhost:8000/health


4. Wysyłaj zapytania:

curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"sonar-pro","messages":[{"role":"user","content":"ping"}]}'



Wdrożenie na Cloudflare Workers

1. Dodaj sekrety w GitHub Secrets:

CF_API_TOKEN

PPLX_KEY_A

PPLX_KEY_B



2. Wypchnij zmiany do gałęzi main.


3. GitHub Actions automatycznie wdroży Worker dzięki plikowi deploy.yml.


4. Po zakończeniu wdrożenia uzyskany URL skopiuj i skonfiguruj w GPT-Codex:

mcp.pplx_mux.set_base_url https://<twoj-worker>.workers.dev



Konfiguracja GPT-Codex (MCP)

W pliku ~/.codex/config.toml dodaj:

[mcp_servers.pplx_mux]
base_url   = "https://<twoj-worker>.workers.dev"
model      = "sonar-pro"
max_tokens = 8192

Testy

Testy uruchamiasz lokalnie komendą:

pytest -q

Licencja

Projekt udostępniony na licencji MIT. Bibeleczność i dozwolone jest używanie dowolnym celu.


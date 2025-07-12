from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import httpx
import os
from typing import List, Dict, Any, AsyncIterator
import asyncio
from enum import Enum

class TrybBalansowania(str, Enum):
    ROUND = "round"
    FAILOVER = "failover"
    DUAL = "dual"

aplikacja = FastAPI(title="Multiplexer API Perplexity")

class MuxPerplexity:
    def __init__(self) -> None:
        self.klucze: List[str] = [
            os.getenv("PPLX_KEY_A"),
            os.getenv("PPLX_KEY_B")
        ]
        self.tryb = TrybBalansowania(os.getenv("MODE", "round"))
        self.indeks_klucza = 0
        self.popsute_klucze: set[str] = set()

    async def pobierz_aktywne_klucze(self) -> List[str]:
        if self.tryb == TrybBalansowania.DUAL:
            return [k for k in self.klucze if k]
        klucz = await self.pobierz_aktywny_klucz()
        return [klucz]

    async def pobierz_aktywny_klucz(self) -> str:
        if self.tryb == TrybBalansowania.ROUND:
            klucz = self.klucze[self.indeks_klucza % len(self.klucze)]
            self.indeks_klucza += 1
            if not klucz:
                raise HTTPException(500, "Brak klucza API")
            return klucz
        if self.tryb == TrybBalansowania.FAILOVER:
            for k in self.klucze:
                if k and k not in self.popsute_klucze:
                    return k
            raise HTTPException(503, "Wszystkie klucze API niedostępne")
        if self.tryb == TrybBalansowania.DUAL:
            klucz = self.klucze[self.indeks_klucza % len(self.klucze)]
            self.indeks_klucza += 1
            if not klucz:
                raise HTTPException(500, "Brak klucza API")
            return klucz
        raise HTTPException(500, "Nieznany tryb")

mux = MuxPerplexity()

async def strumien_odpowiedzi(resp: httpx.Response) -> AsyncIterator[bytes]:
    async for kawalek in resp.aiter_bytes():
        yield kawalek

@aplikacja.get("/health")
async def sprawdz_zdrowie() -> Dict[str, Any]:
    return {"status": "healthy", "mode": mux.tryb}

@aplikacja.post("/chat/completions")
async def proxy_czat(request: Request):
    tresc = await request.json()
    klucze = await mux.pobierz_aktywne_klucze()
    zadania = []
    for klucz in klucze:
        zadania.append(wyslij_zapytanie(tresc, klucz))
    odpowiedzi = await asyncio.gather(*zadania, return_exceptions=True)
    if mux.tryb == TrybBalansowania.DUAL:
        for odp in odpowiedzi:
            if isinstance(odp, httpx.Response) and odp.status_code < 500:
                return StreamingResponse(strumien_odpowiedzi(odp), status_code=odp.status_code, media_type=odp.headers.get("content-type"))
        raise HTTPException(500, "Brak poprawnej odpowiedzi")
    odp = odpowiedzi[0]
    if isinstance(odp, Exception):
        if mux.tryb == TrybBalansowania.FAILOVER:
            mux.popsute_klucze.add(klucze[0])
        raise HTTPException(500, f"Błąd proxy: {str(odp)}")
    return StreamingResponse(strumien_odpowiedzi(odp), status_code=odp.status_code, media_type=odp.headers.get("content-type"))

async def wyslij_zapytanie(body: Dict[str, Any], klucz: str) -> httpx.Response:
    naglowki = {"Authorization": f"Bearer {klucz}"}
    async with httpx.AsyncClient() as klient:
        odp = await klient.post(
            "https://api.perplexity.ai/chat/completions",
            json=body,
            headers=naglowki,
            timeout=None
        )
        return odp

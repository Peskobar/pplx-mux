#!/usr/bin/env python3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "mux" / ".env"

print("Podaj klucz PPLX_KEY_A:")
key_a = input().strip()
print("Podaj klucz PPLX_KEY_B:")
key_b = input().strip()
print("Wybierz tryb (round|failover|dual) [round]:")
mode = input().strip() or "round"

env_content = f"PPLX_KEY_A={key_a}\nPPLX_KEY_B={key_b}\nMODE={mode}\n"
ENV_PATH.write_text(env_content)
print(f"Plik {ENV_PATH} zapisany.")

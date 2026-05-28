"""
Brute-Force Login Attack Demo
==============================
Simulates an attacker trying to guess a user's password via repeated
POST /auth/login requests. The rate limiter (5 req/min) kicks in and
starts returning 429 Too Many Requests after the limit is exceeded.

Usage:
    python attack_brute_force_demo.py [--url http://localhost:8000] [--target user@example.com]
"""

import argparse
import time
import requests

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

WORDLIST = [
    "password", "123456", "qwerty", "letmein", "admin",
    "welcome", "monkey", "dragon", "master", "shadow",
    "sunshine", "princess", "iloveyou", "superman", "batman",
    "football", "baseball", "soccer", "hockey", "tennis",
]


def banner() -> None:
    print(f"""
{BOLD}{RED}╔══════════════════════════════════════════════════════╗
║         BRUTE-FORCE LOGIN ATTACK DEMO               ║
║         CANTTOUCHME — Security Project              ║
╚══════════════════════════════════════════════════════╝{RESET}

{YELLOW}Objetivo:{RESET} Testar múltiplas passwords no endpoint /auth/login
{YELLOW}Defesa:{RESET}   Rate limiting — máximo 5 pedidos/minuto por IP
""")


def attack(base_url: str, target_email: str) -> None:
    url = f"{base_url}/auth/login"

    print(f"{CYAN}[*] Alvo:{RESET}    {target_email}")
    print(f"{CYAN}[*] Endpoint:{RESET} {url}")
    print(f"{CYAN}[*] Wordlist:{RESET} {len(WORDLIST)} passwords")
    print()

    succeeded = 0
    blocked   = 0
    errors    = 0

    for i, password in enumerate(WORDLIST, start=1):
        try:
            t0 = time.monotonic()
            resp = requests.post(
                url,
                json={"email": target_email, "password": password},
                timeout=5,
            )
            elapsed = (time.monotonic() - t0) * 1000

            if resp.status_code == 200:
                succeeded += 1
                print(
                    f"{GREEN}[✓] Tentativa {i:02d}  |  password: {password!r:<14}"
                    f"  →  {resp.status_code} OK  ({elapsed:.0f}ms)  — LOGIN VÁLIDO!{RESET}"
                )
            elif resp.status_code == 401:
                print(
                    f"    Tentativa {i:02d}  |  password: {password!r:<14}"
                    f"  →  {resp.status_code} Unauthorized  ({elapsed:.0f}ms)"
                )
            elif resp.status_code == 429:
                blocked += 1
                retry_after = resp.headers.get("Retry-After", "?")
                print(
                    f"{RED}[!] Tentativa {i:02d}  |  password: {password!r:<14}"
                    f"  →  {resp.status_code} Too Many Requests  ({elapsed:.0f}ms)"
                    f"  —  BLOQUEADO! (retry após {retry_after}s){RESET}"
                )
            else:
                errors += 1
                print(
                    f"{YELLOW}[?] Tentativa {i:02d}  |  password: {password!r:<14}"
                    f"  →  {resp.status_code}  ({elapsed:.0f}ms){RESET}"
                )

        except requests.exceptions.ConnectionError:
            errors += 1
            print(f"{YELLOW}[!] Tentativa {i:02d}  |  Sem ligação ao servidor — está a correr?{RESET}")
            break
        except requests.exceptions.Timeout:
            errors += 1
            print(f"{YELLOW}[!] Tentativa {i:02d}  |  Timeout{RESET}")

        # pequena pausa entre pedidos (mais realista, mas ainda rápido)
        time.sleep(0.1)

    print()
    print(f"{BOLD}══════════════════ SUMÁRIO ══════════════════{RESET}")
    print(f"  Total de tentativas : {len(WORDLIST)}")
    print(f"  {GREEN}Logins bem-sucedidos : {succeeded}{RESET}")
    print(f"  {RED}Pedidos bloqueados   : {blocked}{RESET}")
    print(f"  {YELLOW}Erros / sem resposta : {errors}{RESET}")
    print()

    if blocked > 0:
        print(
            f"{BOLD}{GREEN}[✓] Rate limiting funcionou!{RESET} "
            f"{blocked} pedido(s) bloqueados com 429."
        )
    else:
        print(
            f"{YELLOW}[!] Nenhum pedido foi bloqueado. "
            f"O servidor pode estar sem rate limiting activo.{RESET}"
        )

    if succeeded > 0:
        print(f"{RED}[!] Password encontrada — ver acima.{RESET}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Brute-force login demo com rate limiting")
    parser.add_argument("--url",    default="http://localhost:8000", help="URL base da API")
    parser.add_argument("--target", default="demo@canttouchme.pt",  help="Email do alvo")
    args = parser.parse_args()

    banner()
    attack(args.url, args.target)


if __name__ == "__main__":
    main()

import requests

TOKEN = "token roubado"
r = requests.get(
    "http://localhost:8000/records?page_size=50",
    headers={"Authorization": f"Bearer {TOKEN}"},
    )

dados = r.json()
print(f"Total de registos:{dados['total']}\n")

for reg in dados["records"]:
    print(f"--- Bloco {reg['block_index']} ({reg['timestamp']}) ---")
    print(reg["text"])
    print()
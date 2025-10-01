import requests
from bs4 import BeautifulSoup

url = "https://brasilquecorre.com/santacatarina"

# ignora verificação SSL
pagina = requests.get(url, verify=False)

soup = BeautifulSoup(pagina.text, "html.parser")

widgets = soup.find_all("div", class_="text-editor")

for w in widgets:
    titulo = w.find("h5")
    link = w.find("a", href=True)
    info = w.find_all("p")

    print("🏃 Corrida:", titulo.get_text(strip=True) if titulo else "N/A")
    if info:
        for linha in info:
            texto = linha.get_text(strip=True)
            if texto:  # só imprime se tiver conteúdo
                print("📌", texto)


    print("🔗 Link:", link["href"] if link else "N/A")
    print("-" * 60)
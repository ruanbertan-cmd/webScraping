import requests
from bs4 import BeautifulSoup

url = "https://brasilquecorre.com/santacatarina"
pagina = requests.get(url)
pagina.encoding = "utf-8"

soup = BeautifulSoup(pagina.text, "html.parser")

# encontra todos os blocos de eventos
widgets = soup.find_all("div", class_="cs-widgets")

for w in widgets:
    # nome da corrida (geralmente no <h3>)
    titulo = w.find("h5")
    # link do evento (primeiro <a>)
    link = w.find("a", href=True)
    # data e local (geralmente ficam em <p> ou <span>)
    info = w.find_all("p")

    print("🏃 Corrida:", titulo.get_text(strip=True) if titulo else "N/A")
    if info:
        for linha in info:
            print("📌", linha.get_text(strip=True))
    print("🔗 Link:", link["href"] if link else "N/A")
    print("-" * 60)

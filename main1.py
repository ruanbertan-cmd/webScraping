import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

url = "https://www.corridasbr.com.br/sc/Calendario.asp"

# ignora verificação SSL
pagina = requests.get(url, verify=False)

soup = BeautifulSoup(pagina.text, "html.parser")

widgets = soup.find_all("tr", class_="tipo4")

for w in widgets:
    # pega todos os <a>
    links = w.find_all("a", href=True)

    # pega o título (segundo <a>)
    titulo = links[1].get_text(strip=True) if len(links) > 1 else "N/A"

    # trata o segundo link
    if len(links) > 1:
        raw_link = links[1]["href"]

        # separa base e texto depois do &
        if "&" in raw_link:
            base, texto = raw_link.split("&", 1)
            segundo_link = f"{base}&{quote(texto)}"
        else:
            segundo_link = raw_link
    else:
        segundo_link = "N/A"

    info = w.find_all("td")

    print("🏃 Corrida:", titulo)
    if info:
        for linha in info:
            texto = linha.get_text(strip=True)
            if texto:
                print("📌", texto)

    print("🔗 Segundo link: https://www.corridasbr.com.br/sc/" + segundo_link)
    print("-" * 60)


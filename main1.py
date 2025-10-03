import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
import urllib3

# Ignora warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://www.corridasbr.com.br/sc/Calendario"
extensao = ".asp"

pagina_num = 0  # Começa na página principal

while True:
    if pagina_num == 0:
        url = f"{base_url}{extensao}"
    else:
        url = f"{base_url}{pagina_num}{extensao}"

    pagina = requests.get(url, verify=False)
    if pagina.status_code != 200:
        break

    soup = BeautifulSoup(pagina.text, "html.parser")
    trs = soup.find_all("tr", class_="tipo4")
    if not trs:
        break

    for w in trs:
        links = w.find_all("a", href=True)
        titulo = links[1].get_text(strip=True).upper() if len(links) > 1 else "N/A"

        if len(links) > 1:
            raw_link = links[1]["href"]
            if "&" in raw_link:
                base, texto = raw_link.split("&", 1)
                segundo_link = f"{base}&{quote(texto)}"
            else:
                segundo_link = raw_link
        else:
            segundo_link = "N/A"

        link_evento = "https://www.corridasbr.com.br/sc/" + segundo_link

        # ---------------------------
        # Acessa a página do evento para pegar a data real
        pagina_evento = requests.get(link_evento, verify=False)
        soup_evento = BeautifulSoup(pagina_evento.text, "html.parser")

        # Extrai apenas a data no formato dd/mm/yyyy
        data_real = "N/A"
        for td in soup_evento.find_all("td"):
            texto = td.get_text(strip=True)
            match = re.search(r'\d{2}/\d{2}/\d{4}', texto)
            if match:
                data_real = match.group()
                break

        # ---------------------------
        info = w.find_all("td")
        # Cidade e distância geralmente estão em td[2] e td[3]
        cidade = info[1].get_text(strip=True) if len(info) > 1 else "N/A"
        distancia = info[3].get_text(strip=True) if len(info) > 3 else "N/A"

        # Impressão final no formato desejado
        print("🏃 Corrida:", titulo)
        print("📌", data_real)
        print("📌", cidade)
        print("📌", distancia)
        print("🔗 Link do evento:", link_evento)
        print("-" * 60)

    pagina_num += 1
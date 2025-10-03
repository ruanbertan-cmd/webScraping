import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
import urllib3

# Ignora warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------------- Lista de eventos únicos -------------------
eventos_unicos = []

# Função para checar duplicidade
def ja_existe(titulo, data):
    for e in eventos_unicos:
        if e['titulo'].lower() == titulo.lower() and e['data'] == data:
            return True
    return False

# ------------------- Site 1: brasilquecorre.com -------------------
url1 = "https://brasilquecorre.com/santacatarina"
pagina1 = requests.get(url1, verify=False)
soup1 = BeautifulSoup(pagina1.text, "html.parser")

widgets = soup1.find_all("div", class_="text-editor") + soup1.find_all("article")

meses = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}

for w in widgets:
    titulo_tag = w.find("h5") or w.find("h2") or w.find("h3")
    link_tag = w.find("a", href=True)
    info_tags = w.find_all("p") or w.find_all("li")

    titulo = titulo_tag.get_text(strip=True) if titulo_tag else "N/A"

    data_evento = None
    cidade = "N/A"
    distancia = "N/A"

    if info_tags:
        for linha in info_tags:
            texto = linha.get_text(strip=True)
            if not texto or (texto.isupper() and texto != titulo):
                continue
            match = re.search(r'(\d{1,2}) de (\w+) de (\d{4})', texto)
            if match:
                dia, mes_txt, ano = match.groups()
                mes_num = meses.get(mes_txt.lower())
                if mes_num:
                    data_evento = f"{int(dia):02d}/{mes_num:02d}/{ano}"
            elif data_evento:
                # Tenta pegar cidade ou distância se houver data
                if "km" in texto.lower():
                    distancia = texto
                else:
                    cidade = texto

    if data_evento and not ja_existe(titulo, data_evento):
        eventos_unicos.append({
            "titulo": titulo,
            "data": data_evento,
            "cidade": cidade,
            "distancia": distancia,
            "link": link_tag["href"] if link_tag else "N/A"
        })

# ------------------- Site 2: corridasbr.com.br -------------------
base_url = "https://www.corridasbr.com.br/sc/Calendario"
extensao = ".asp"
pagina_num = 0

while True:
    if pagina_num == 0:
        url2 = f"{base_url}{extensao}"
    else:
        url2 = f"{base_url}{pagina_num}{extensao}"

    pagina = requests.get(url2, verify=False)
    if pagina.status_code != 200:
        break

    soup2 = BeautifulSoup(pagina.text, "html.parser")
    trs = soup2.find_all("tr", class_="tipo4")
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

        # Pega data real
        pagina_evento = requests.get(link_evento, verify=False)
        soup_evento = BeautifulSoup(pagina_evento.text, "html.parser")
        data_real = "N/A"
        for td in soup_evento.find_all("td"):
            texto = td.get_text(strip=True)
            match = re.search(r'\d{2}/\d{2}/\d{4}', texto)
            if match:
                data_real = match.group()
                break

        info = w.find_all("td")
        cidade = info[1].get_text(strip=True) if len(info) > 1 else "N/A"
        distancia = info[3].get_text(strip=True) if len(info) > 3 else "N/A"

        if data_real != "N/A" and not ja_existe(titulo, data_real):
            eventos_unicos.append({
                "titulo": titulo,
                "data": data_real,
                "cidade": cidade,
                "distancia": distancia,
                "link": link_evento
            })

    pagina_num += 1

# ------------------- Impressão final -------------------
for e in eventos_unicos:
    print("🏃 Corrida:", e["titulo"])
    print("📌", e["data"])
    print("📌", e["cidade"])
    print("📌", e["distancia"])
    print("🔗 Link:", e["link"])
    print("-" * 60)

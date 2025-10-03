import requests
from bs4 import BeautifulSoup
import re

url = "https://brasilquecorre.com/santacatarina"

# Ignora warnings SSL
requests.packages.urllib3.disable_warnings()

pagina = requests.get(url, verify=False)
soup = BeautifulSoup(pagina.text, "html.parser")

# Captura containers de eventos
widgets = soup.find_all("div", class_="text-editor") + soup.find_all("article")

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

    texto_com_data = []
    if info_tags:
        for linha in info_tags:
            texto = linha.get_text(strip=True)
            if not texto:
                continue

            # Ignora linhas totalmente maiúsculas diferentes do título
            if texto.isupper() and texto != titulo:
                continue

            # Procura datas no formato "11 de outubro de 2025"
            match = re.search(r'(\d{1,2}) de (\w+) de (\d{4})', texto)
            if match:
                dia, mes_txt, ano = match.groups()
                mes_num = meses.get(mes_txt.lower())
                if mes_num:
                    texto_formatado = re.sub(
                        r'\d{1,2} de \w+ de \d{4}',
                        f"{int(dia):02d}/{mes_num:02d}/{ano}",
                        texto
                    )
                    texto_com_data.append(texto_formatado)
            else:
                # Mantém outras linhas (como cidade, distância) se já houver uma data no evento
                if texto_com_data:
                    texto_com_data.append(texto)

    # Só exibe o evento se tiver pelo menos uma data
    if texto_com_data:
        print("🏃 Corrida:", titulo)
        for t in texto_com_data:
            print("📌", t)
        print("🔗 Link:", link_tag["href"] if link_tag else "N/A")
        print("-" * 60)

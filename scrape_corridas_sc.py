# -*- coding: utf-8 -*-
"""
Scrape básico de eventos de corrida de rua em Santa Catarina (BR)
Versão ajustada para Windows / SSL / DataFrame vazio
"""

import re
import json
from datetime import datetime
from dateutil import parser as dateparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import urllib3

# Suprimir warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RuanBot/1.0; +https://example.com)"
}

SOURCES = [
    "https://socorridas.com.br/corrida/santa-catarina/",
    "https://www.atletis.com.br/busca?estado=SC",
    "https://supercrono.com.br/resultados-eventos/",
    "https://www.corridasbr.com.br/SC/Calendario.asp",
    "https://inscricoes.focoradical.com.br/provas/estado/sc",
    "https://www.catarinarun.com.br/",
    "https://www.correbrasil.com.br/calendario-corridas"
]

PRICE_RE = re.compile(r"R\$\s?[\d\.,]+", re.IGNORECASE)
DATE_RE = re.compile(r"(\d{1,2}\s*[/\-]\s*\d{1,2}\s*[/\-]\s*\d{2,4}|\d{1,2}\s*/\s*\d{1,2}|\d{1,2}\s*(de)?\s*[A-Za-z]+(?:\s*de\s*\d{4})?)", re.IGNORECASE)

def get_soup(url, timeout=12):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"[ERRO] ao acessar {url}: {e}")
        return None

def find_price(text):
    if not text:
        return None
    m = PRICE_RE.search(text)
    return m.group(0) if m else None

def find_date(text):
    if not text:
        return None
    m = DATE_RE.search(text)
    if not m:
        return None
    s = m.group(0)
    try:
        dt = dateparser.parse(s, dayfirst=True, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return s.strip()

def extract_from_link_tag(a, base_url):
    title = (a.get_text(separator=" ", strip=True) or "").strip()
    href = a.get("href") or a.get("data-href") or ""
    link = urljoin(base_url, href) if href else base_url
    surrounding = " ".join([t.get_text(separator=" ", strip=True) for t in a.find_all_next(limit=6)]) if a else ""
    combined = f"{title} {surrounding}"
    price = find_price(combined)
    date = find_date(combined)
    city = None
    m_city = re.search(r"([A-Za-z\u00C0-\u017F ]+)[\s,-]+SC\b", combined)
    if m_city:
        city = m_city.group(1).strip()
    return {
        "title": title,
        "link": link,
        "date": date,
        "price": price,
        "city": city
    }

def parse_generic_index(url):
    soup = get_soup(url)
    if not soup:
        return []
    results = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True).lower()
        href = a["href"]
        if any(k in text for k in ("corrid", "run", "meia", "10k", "5k", "5 km", "10 km")) or "/event" in href:
            results.append(extract_from_link_tag(a, url))
    return results

PARSERS = {
    "socorridas.com.br": parse_generic_index,
    "atletis.com.br": parse_generic_index,
    "supercrono.com.br": parse_generic_index,
    "corridasbr.com.br": parse_generic_index,
    "inscricoes.focoradical.com.br": parse_generic_index,
    "catarinarun.com.br": parse_generic_index,
    "correbrasil.com.br": parse_generic_index
}

def choose_parser(url):
    for domain, func in PARSERS.items():
        if domain in url:
            return func
    return parse_generic_index

def scrape_all():
    found = []
    failed = []
    for src in SOURCES:
        print(f"[INFO] buscando {src}")
        parser = choose_parser(src)
        try:
            items = parser(src)
            print(f"  -> achou {len(items)} itens (heurística)")
            for it in items:
                if not it.get("title"):
                    continue
                found.append(it)
        except Exception as e:
            print(f"[ERRO] parser para {src} falhou: {e}")
            failed.append({"url": src, "error": str(e)})
    unique = {}
    for it in found:
        key = (it.get("link") or it.get("title")).strip()
        if key not in unique:
            unique[key] = it
    results = list(unique.values())
    return results, failed

def postprocess(results):
    for r in results:
        if not r.get("date"):
            try:
                ev_soup = get_soup(r["link"])
                if ev_soup:
                    txt = ev_soup.get_text(" ", strip=True)
                    r["price"] = r.get("price") or find_price(txt)
                    r["date"] = r.get("date") or find_date(txt)
                    m_city = re.search(r"([A-Za-z\u00C0-\u017F ]+)[\s,-]+SC\b", txt)
                    if m_city:
                        r["city"] = r.get("city") or m_city.group(1).strip()
            except Exception:
                pass
    return results

def main():
    results, failed = scrape_all()
    results = postprocess(results)
    
    if not results:
        print("[WARN] Nenhum evento encontrado. Verifique conexão/SSL ou URLs.")
        return
    
    df = pd.DataFrame(results)
    df = df.rename(columns={
        "title": "event",
        "city": "local",
        "date": "date",
        "price": "valor_inscricao",
        "link": "link"
    })
    df = df[["event", "local", "date", "valor_inscricao", "link"]]
    
    df.to_csv("events_sc.csv", index=False, encoding="utf-8-sig")
    with open("events_sc.json", "w", encoding="utf-8") as f:
        f.write(df.to_json(orient="records", force_ascii=False, date_format="iso"))
    
    print(f"[OK] Salvo {len(df)} eventos em events_sc.csv e events_sc.json")
    if failed:
        print("[WARN] Algumas fontes falharam no parse (ver log):")
        for f in failed:
            print(" -", f)
    else:
        print("[INFO] Nenhuma falha crítica.")

if __name__ == "__main__":
    main()

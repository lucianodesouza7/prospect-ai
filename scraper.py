"""
Motor de Web Scraping para prospecção de clientes.
Usa Selenium para buscar empresas no Google Maps.
"""

import time
import re
import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None


def _criar_driver():
    """Cria e retorna uma instância do Chrome WebDriver configurada para produção."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Detectar se estamos no Streamlit Cloud (Linux) ou local (Windows)
    if platform.system() == "Linux":
        # Streamlit Cloud – chromedriver do packages.txt
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        # Local – webdriver-manager baixa automaticamente
        if ChromeDriverManager is not None:
            service = Service(ChromeDriverManager().install())
        else:
            service = Service()

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    return driver


def limpar_numero(telefone: str) -> str:
    """Remove caracteres não numéricos e adiciona código do país +55."""
    num = re.sub(r"\D", "", str(telefone))
    if not num:
        return ""
    if not num.startswith("55") and len(num) >= 10:
        num = "55" + num
    return num


def _extrair_email_do_site(driver, url: str) -> str:
    """Visita o site da empresa e tenta encontrar um e-mail de contato."""
    if not url or url in ("—", "N/A", ""):
        return ""
    try:
        driver.execute_script(f"window.open('{url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)
        page_source = driver.page_source
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page_source
        )
        # Filtrar e-mails genéricos (imagens, scripts, etc.)
        emails_validos = [
            e
            for e in emails
            if not e.endswith((".png", ".jpg", ".gif", ".svg", ".webp"))
            and "sentry" not in e.lower()
            and "example" not in e.lower()
            and "wixpress" not in e.lower()
        ]
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return emails_validos[0] if emails_validos else ""
    except Exception:
        # Garantir que voltamos à janela principal
        try:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception:
            pass
        return ""


def _scroll_painel_resultados(driver, scroll_count: int = 5):
    """Rola o painel lateral de resultados do Google Maps para carregar mais itens."""
    try:
        # Tentar encontrar o painel scrollável de resultados
        scrollable_div = driver.find_element(
            By.CSS_SELECTOR, 'div[role="feed"]'
        )
        for _ in range(scroll_count):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div
            )
            time.sleep(1.5)
    except NoSuchElementException:
        # Fallback: scroll na página inteira
        for _ in range(scroll_count):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1.5)


def buscar_empresas(
    segmento: str,
    localizacao: str,
    max_resultados: int = 20,
    buscar_emails: bool = False,
    progress_callback=None,
) -> list[dict]:
    """
    Busca empresas no Google Maps e retorna uma lista de dicionários com:
    Nome, Telefone, Endereço, Site, Avaliação.

    Args:
        segmento: Tipo de negócio (ex: "Restaurantes", "Academias").
        localizacao: Cidade ou região (ex: "São Paulo", "Porto Alegre - RS").
        max_resultados: Número máximo de resultados para extrair.
        buscar_emails: Se True, visita o site de cada empresa para buscar e-mail.
        progress_callback: Função opcional (current, total) para reportar progresso.

    Returns:
        Lista de dicts com dados de cada empresa encontrada.
    """
    driver = None
    dados = []

    try:
        driver = _criar_driver()
        query = f"{segmento} em {localizacao}"
        url_maps = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        driver.get(url_maps)

        # Esperar carregar os resultados (espera explícita)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
            )
        except TimeoutException:
            # Pode ser que a página carregou de forma diferente
            time.sleep(5)

        # Scroll para carregar mais resultados
        scroll_rounds = max(3, max_resultados // 5)
        _scroll_painel_resultados(driver, scroll_count=scroll_rounds)
        time.sleep(2)

        # Coletar links de cada resultado
        links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
        # Filtrar links duplicados
        urls_unicas = []
        seen = set()
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and href not in seen:
                    seen.add(href)
                    urls_unicas.append(href)
            except StaleElementReferenceException:
                continue

        urls_unicas = urls_unicas[:max_resultados]
        total = len(urls_unicas)

        for idx, url in enumerate(urls_unicas):
            try:
                driver.get(url)
                time.sleep(2.5)  # Pausa para evitar bloqueio

                # Extrair nome
                nome = ""
                try:
                    el_nome = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h1.DUwDvf, h1.fontHeadlineLarge")
                        )
                    )
                    nome = el_nome.text.strip()
                except TimeoutException:
                    try:
                        el_nome = driver.find_element(By.CSS_SELECTOR, "h1")
                        nome = el_nome.text.strip()
                    except NoSuchElementException:
                        nome = "Sem nome"

                # Extrair informações do painel de detalhes
                telefone = ""
                endereco = ""
                site = ""
                avaliacao = ""

                # Telefone
                try:
                    el_phone = driver.find_element(
                        By.CSS_SELECTOR,
                        'button[data-item-id*="phone"] div.fontBodyMedium, '
                        'a[data-item-id*="phone"] div.fontBodyMedium',
                    )
                    telefone = el_phone.text.strip()
                except NoSuchElementException:
                    # Fallback: buscar pelo ícone de telefone
                    try:
                        elementos = driver.find_elements(
                            By.CSS_SELECTOR, 'button[data-tooltip="Copiar o número de telefone"]'
                        )
                        if elementos:
                            telefone = elementos[0].get_attribute("aria-label") or ""
                            telefone = telefone.replace("Telefone:", "").strip()
                    except Exception:
                        pass

                # Endereço
                try:
                    el_addr = driver.find_element(
                        By.CSS_SELECTOR,
                        'button[data-item-id="address"] div.fontBodyMedium, '
                        'button[data-item-id="address"] div.Io6YTe',
                    )
                    endereco = el_addr.text.strip()
                except NoSuchElementException:
                    try:
                        elementos = driver.find_elements(
                            By.CSS_SELECTOR, 'button[data-tooltip="Copiar endereço"]'
                        )
                        if elementos:
                            endereco = elementos[0].get_attribute("aria-label") or ""
                            endereco = endereco.replace("Endereço:", "").strip()
                    except Exception:
                        pass

                # Site
                try:
                    el_site = driver.find_element(
                        By.CSS_SELECTOR,
                        'a[data-item-id="authority"] div.fontBodyMedium, '
                        'a[data-item-id="authority"] div.Io6YTe',
                    )
                    site = el_site.text.strip()
                except NoSuchElementException:
                    try:
                        el_link = driver.find_element(
                            By.CSS_SELECTOR, 'a[data-item-id="authority"]'
                        )
                        site = el_link.get_attribute("href") or ""
                    except NoSuchElementException:
                        pass

                # Avaliação
                try:
                    el_rating = driver.find_element(
                        By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']"
                    )
                    avaliacao = el_rating.text.strip()
                except NoSuchElementException:
                    pass

                # E-mail (opcional – visita o site)
                email = ""
                if buscar_emails and site:
                    site_url = site if site.startswith("http") else f"https://{site}"
                    email = _extrair_email_do_site(driver, site_url)

                empresa = {
                    "Nome": nome if nome else "Sem nome",
                    "Telefone": telefone if telefone else "—",
                    "Endereço": endereco if endereco else "—",
                    "Site": site if site else "—",
                    "Avaliação": avaliacao if avaliacao else "—",
                    "E-mail": email if email else "—",
                    "Status": "🆕 Novo",
                }

                dados.append(empresa)

                if progress_callback:
                    progress_callback(idx + 1, total)

            except (TimeoutException, WebDriverException) as e:
                # Pular este resultado e continuar
                continue

            # Pausa entre requisições para evitar bloqueio
            time.sleep(1)

    except WebDriverException as e:
        raise RuntimeError(
            f"Erro ao iniciar o navegador: {str(e)}. "
            "Verifique se o Chrome/Chromium está instalado."
        )
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return dados

import os
import json
import pandas as pd
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES

# Configurações do Selenium
usuario = os.getenv("USERPROFILE")
geckodriver_path = rf"C:\Cinemato.Graphy\geckodriver.exe"
firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options = Options()
options.binary_location = firefox_path

def iniciar_bot(caminho_arquivo, caixa_status):
    caixa_status.insert(tk.END, f"Lendo arquivo: {caminho_arquivo}\n")
    try:
        filmes_df = pd.read_csv(caminho_arquivo, header=None, encoding='utf-8')
    except Exception as e:
        caixa_status.insert(tk.END, f"Erro ao ler arquivo: {e}\n")
        return

    try:
        driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)
        driver.maximize_window()
    except WebDriverException as e:
        caixa_status.insert(tk.END, f"Erro ao iniciar o navegador: {e}\n")
        return

    def safe_xpath(xpath):
        try:
            element = driver.find_element(By.XPATH, xpath)
            return element.text.strip() if element.text.strip() else "Não encontrado"
        except NoSuchElementException:
            return "Não encontrado"

    dados_filmes = []
    for _, row in filmes_df.iterrows():
        nome = row[0].strip()
        caixa_status.insert(tk.END, f"🔍 Buscando: {nome}\n")
        try:
            driver.get("https://www.imdb.com/")
            sleep(2)

            campo_busca = driver.find_element(By.XPATH, '//*[@id="suggestion-search"]')
            campo_busca.clear()
            campo_busca.send_keys(nome)
            campo_busca.send_keys(Keys.ENTER)
            sleep(3)

            primeiro = driver.find_element(By.XPATH, '//ul[contains(@class, "ipc-metadata-list")]/li[1]//a')
            primeiro.click()
            sleep(3)

            for _ in range(6):
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                sleep(0.2)

            sleep(5)

            nota = safe_xpath('//span[contains(@class, "sc-") and contains(@class, "rating")]/span[1]')
            ano = safe_xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[1]/a')
            duracao = safe_xpath('//ul[contains(@class, "ipc-inline-list")]/li[contains(., "h") or contains(., "min")]')
            diretor = safe_xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/ul/li[1]/div/ul/li/a')
            descricao = safe_xpath('//span[contains(@data-testid, "plot-xl")]')
            href = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[5]/div[1]/div/a').get_attribute('href')
            estrela = driver.find_element(By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a').get_attribute('href')

            try:
                poster = driver.find_element(By.CSS_SELECTOR, "[data-testid='hero-media__poster']").find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                poster = "Não encontrado"

        
            dados_filmes.append({
                "name": nome,
                "gender": " ",
                "banner": poster,
                "sinopse": descricao,
                "year": ano,
                "duration": duracao,
                "director": diretor,
                "assesment": nota,
                "link": href,
                "star": estrela
            })

            caixa_status.insert(tk.END, f"✅ {nome} coletado\n")
        except Exception as e:
            caixa_status.insert(tk.END, f"⚠️ Erro com {nome}: {e}\n")
            continue

    driver.quit()

    caminho_json = os.path.splitext(caminho_arquivo)[0] + "_filmes.json"
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(dados_filmes, f, ensure_ascii=False, indent=4)

    caixa_status.insert(tk.END, f"\n💾 JSON salvo: {caminho_json}\n")

    url = "https://faculdade-cv39.onrender.com/movie"
    for filme in dados_filmes:
        resp = requests.post(url, json=filme)
        if resp.status_code in [200, 201]:
            caixa_status.insert(tk.END, f"✅ Enviado: {filme['name']}\n")
        else:
            caixa_status.insert(tk.END, f"❌ Erro: {filme['name']} ({resp.status_code})\n")
        sleep(1)

# Interface Tkinter
def criar_interface():
    root = TkinterDnD.Tk()
    root.title("🎬 Bot de Filmes - IMDB Scraper")
    root.geometry("600x500")
    root.resizable(False, False)
    root.configure(bg="#1e1e1e")

    ttk.Style().theme_use('clam')

    titulo = tk.Label(root, text="Arraste o arquivo .txt com os nomes dos filmes", fg="#fff", bg="#1e1e1e", font=("Helvetica", 14))
    titulo.pack(pady=10)

    drop_area = tk.Label(root, text="⬇️ Solte aqui o arquivo", relief="groove", width=50, height=4, bg="#333", fg="white", font=("Arial", 12))
    drop_area.pack(pady=20)

    status = tk.Text(root, height=15, width=70, bg="#121212", fg="white")
    status.pack(pady=10)

    def drop(event):
        caminho = event.data.strip("{}")
        status.insert(tk.END, f"📁 Arquivo recebido: {caminho}\n")
        iniciar_bot(caminho, status)

    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", drop)

    root.mainloop()

criar_interface()

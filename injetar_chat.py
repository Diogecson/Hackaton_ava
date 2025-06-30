# injetar_chat.py
from selenium import webdriver
import time

# 🚀 Abre o navegador e acessa Brightspace
navegador = webdriver.Chrome()
navegador.get("https://fecaf.brightspace.com/d2l/login")
input("🔓 Faça login na Brightspace e pressione ENTER...")

# Espera a página carregar
time.sleep(2)

# URL do Gradio (pode ser local ou gerado pelo `share=True`)
iframe_url = "https://SEU_LNK_DO_GRADIO.gradio.live"  # Atualize com a URL gerada

# JavaScript para injetar o balão de chat
script = f"""
if (!document.getElementById('chatbot-widget')) {{
    let iframe = document.createElement('iframe');
    iframe.id = 'chatbot-widget';
    iframe.src = '{iframe_url}';
    iframe.style.position = 'fixed';
    iframe.style.bottom = '20px';
    iframe.style.right = '20px';
    iframe.style.width = '380px';
    iframe.style.height = '500px';
    iframe.style.border = 'none';
    iframe.style.borderRadius = '16px';
    iframe.style.zIndex = '9999';
    iframe.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
    document.body.appendChild(iframe);
}}
"""

navegador.execute_script(script)
print("✅ Chatbot injetado com sucesso!")

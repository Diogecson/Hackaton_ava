from selenium import webdriver
from bs4 import BeautifulSoup
import time

# Abre o navegador
navegador = webdriver.Chrome()
print("🔓 Faça o login manualmente no navegador que abriu.")
print("👉 Após acessar a página desejada, volte aqui e pressione ENTER.")

input("⏳ Aguardando... Pressione ENTER quando estiver logado e na página certa.")

# Aguarda e captura o HTML da página atual
html = navegador.page_source
soup = BeautifulSoup(html, "html.parser")
for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
    tag.decompose()
texto = ' '.join(soup.stripped_strings)

# Salva o texto
with open("pagina_extraida.txt", "w", encoding="utf-8") as f:
    f.write(texto)

print("✅ Conteúdo extraído e salvo em 'pagina_extraida.txt'.")
input("Pressione ENTER para fechar o navegador.")
navegador.quit()

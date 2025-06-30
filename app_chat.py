import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import gradio as gr

# Configurar API do Gemini
genai.configure(api_key="AIzaSyBrBUx_sHejHnSw159EYGc1olIiJWmBLIA")
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Extrair texto da URL ou de arquivo local
def extrair_texto(url):
    try:
        if url.startswith("arquivo://"):
            with open("pagina_extraida.txt", "r", encoding="utf-8") as f:
                return f.read()
        else:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
                tag.decompose()
            texto = ' '.join(soup.stripped_strings)
            return texto[:20000]
    except:
        return None

# Estado global: conteúdo da página
conteudo_global = {"texto": ""}

# Função para chat com retorno do estado
def chat(url, pergunta, historico):
    if not conteudo_global["texto"] or (historico and url != historico[0][0]):
        texto = extrair_texto(url)
        if not texto:
            return historico + [[url, "Erro ao carregar a página."]], historico
        conteudo_global["texto"] = texto
        historico = [[url, "Página carregada. Você pode perguntar algo sobre ela."]]

    prompt = f"Com base no conteúdo abaixo, responda a pergunta:\n\n{conteudo_global['texto']}\n\nPergunta: {pergunta}"
    resposta = model.generate_content([prompt]).text
    historico.append([pergunta, resposta])
    return historico, historico



# Atualize o chatbot e interface com estado corretamente
chatbot = gr.Chatbot(label="Chat sobre a página", type="tuples")
url_input = gr.Textbox(label="Cole a URL da página", placeholder="https://exemplo.com")
pergunta_input = gr.Textbox(label="Pergunte algo sobre a página", placeholder="Ex: Qual a ideia principal?")

demo = gr.Interface(
    fn=chat,
    inputs=[url_input, pergunta_input, gr.State([])],
    outputs=[chatbot, gr.State()],
    title="Resumo e Chat com a Página 🌐🧠",
    description="Cole uma URL, e depois pergunte sobre o conteúdo como se fosse um chat!"
)


if __name__ == "__main__":
    demo.launch()

import gradio as gr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai

# Configurar Gemini
genai.configure(api_key="AIzaSyDSdPnPh2dVOXd_94e0PQFD9jVC8JECz6I")  # Substitua pela sua chave da API
model = genai.GenerativeModel("gemini-1.5-flash")

# Iniciar navegador (mantendo a aba aberta e sem notificações)
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
navegador = webdriver.Chrome(options=chrome_options)
navegador.get("https://fecaf.brightspace.com/d2l/login")
input("🔐 Faça o login e pressione ENTER para continuar...")

# Esperar o conteúdo principal carregar
try:
    WebDriverWait(navegador, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "d2l-page-main"))
    )
except:
    print("⚠️ Timeout ao esperar conteúdo da Brightspace. Verifique o login.")

# Conteúdo global
conteudo_global = {"texto": "", "topicos": []}

def atualizar_conteudo():
    try:
        # Captura todos os elementos visíveis e ignora scripts, headers, etc.
        elementos = navegador.find_elements(By.XPATH, "//*[not(self::script or self::style or self::header or self::footer or self::nav or self::aside)]")
        textos_visiveis = []

        for el in elementos:
            if el.is_displayed():
                texto = el.text.strip()
                if texto:
                    textos_visiveis.append(texto)

        texto_final = ' '.join(textos_visiveis)[:20000]
        conteudo_global["texto"] = texto_final

        prompt_resumo = f"Leia o conteúdo abaixo da página e aponte um RESUMO e principais TÓPICOS:\n\n{texto_final}"
        resposta = model.generate_content(prompt_resumo).text
        conteudo_global["topicos"] = resposta
        return "✅ Conteúdo visível atualizado com sucesso!"
    except Exception as e:
        return f"❌ Erro ao atualizar: {e}"

def chat(pergunta, historico):
    if not conteudo_global["texto"]:
        return [["Sistema", "Você precisa clicar em Atualizar antes de perguntar."]], []

    historico_texto = "\n".join(f"Usuário: {p}\nIA: {r}" for p, r in historico)
    prompt = (
        f"Conteúdo da página:\n{conteudo_global['texto']}\n\n"
        f"Tópicos:\n{conteudo_global['topicos']}\n\n"
        f"Histórico:\n{historico_texto}\n\n"
        f"Nova pergunta:\n{pergunta}"
    )

    resposta = model.generate_content(prompt).text
    historico.append([pergunta, resposta])
    return historico, historico

# Interface com Gradio
with gr.Blocks(css="""
    .gradio-container { font-family: 'Arial', sans-serif; }
    #chatbot { height: 400px; }
    .gr-button { border-radius: 8px !important; }
""") as demo:

    gr.Image("lobinho.gif", show_label=False, show_download_button=False)

    chatbot = gr.Chatbot(elem_id="chatbot", label="Lobinho IA")
    entrada = gr.Textbox(placeholder="Digite sua dúvida...", label="", lines=2)

    with gr.Row():
        btn_atualizar = gr.Button("🔄 Atualizar")
        btn_enviar = gr.Button("📨 Enviar")
        btn_sair = gr.Button("🚪 Sair")

    status = gr.Textbox(label="Status", max_lines=1, interactive=False)

    btn_atualizar.click(fn=atualizar_conteudo, inputs=[], outputs=[status])
    entrada.submit(fn=chat, inputs=[entrada, chatbot], outputs=[chatbot, chatbot])
    btn_enviar.click(fn=chat, inputs=[entrada, chatbot], outputs=[chatbot, chatbot])
    btn_sair.click(fn=lambda: exit(), inputs=[], outputs=[])


# Roda app
if __name__ == "__main__":
    demo.launch()
    navegador.quit()

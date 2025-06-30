import gradio as gr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai
import time

# Configurar Gemini
genai.configure(api_key="SUA_CHAVE_DO_GEMINI")  # Substitua pela sua chave
model = genai.GenerativeModel("gemini-1.5-flash")

# Configurar Chrome em modo headless para Render
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

navegador = webdriver.Chrome(options=chrome_options)
navegador.get("https://fecaf.brightspace.com/d2l/login")

# Aguarda tempo para login manual (caso queira testar com conta pública)
time.sleep(15)

# Esperar o conteúdo principal carregar
try:
    WebDriverWait(navegador, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "d2l-page-main"))
    )
except:
    print("⚠️ Timeout ao esperar conteúdo da Brightspace.")

# Conteúdo global
conteudo_global = {"texto": "", "topicos": []}

def atualizar_conteudo():
    try:
        elementos = navegador.find_elements(By.XPATH, "//*[not(self::script or self::style or self::header or self::footer or self::nav or self::aside)]")
        textos_visiveis = [el.text.strip() for el in elementos if el.is_displayed() and el.text.strip()]
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

# Interface Gradio
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

# Executa o app na porta da Render
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
    navegador.quit()

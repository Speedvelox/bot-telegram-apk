
import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# PEGA 100% DO RENDER - SEM FALLBACK VAZADO
TOKEN = os.environ.get("8988527445:AAH0FJAwyLgN56twnCxJManVpCfQBghI8")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN nao definido no Environment do Render!")

DONO_ID = int(os.environ.get("DONO_ID", "7599067084"))
CANAL_BANCO_DADOS = int(os.environ.get("CANAL_BANCO_DADOS", "-1004358687748"))
CANAL_OBRIGATORIO = os.environ.get("CANAL_OBRIGATORIO", "@lcmodsrepoo")

bot = telebot.TeleBot(TOKEN)
downloads_pendentes = {}

# === SERVIDOR FAKE PARA O RENDER NAO DERRUBAR ===
app_web = Flask(__name__)
@app_web.route('/')
def health():
    return "Bot online!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

Thread(target=run_web, daemon=True).start()
# ================================================

def checar_inscricao(user_id):
    try:
        status = bot.get_chat_member(CANAL_OBRIGATORIO, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Erro checar_inscricao: {e}")
        return False

def menu_apks():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📦 BMWA_GB", callback_data="apk_bmwa_gb"),
        InlineKeyboardButton("📦 BMWA_WA", callback_data="apk_bmwa_wa")
    )
    markup.row(
        InlineKeyboardButton("🖤 BMWA_GB_AMOLED", callback_data="apk_bmwa_gb_amoled"),
        InlineKeyboardButton("🖤 BMWA_WA_AMOLED", callback_data="apk_bmwa_wa_amoled")
    )
    markup.row(InlineKeyboardButton("🔄 Refresh", callback_data="refresh_menu"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    args = message.text.split()
    user_id = message.chat.id
    if len(args) > 1:
        id_mensagem_apk = args[1]
        downloads_pendentes[user_id] = id_mensagem_apk
        if checar_inscricao(user_id):
            bot.send_message(user_id, "⌛ Enviando o seu APK, aguarde...")
            try:
                bot.copy_message(user_id, CANAL_BANCO_DADOS, int(id_mensagem_apk))
            except Exception as e:
                print(f"Erro copy: {e}")
                bot.send_message(user_id, "❌ Erro ao enviar arquivo. Verifique se o Bot é ADM do canal privado.")
        else:
            markup = InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton("➕ Entrar no Canal", url=f"https://t.me/{CANAL_OBRIGATORIO.replace('@','')}"))
            markup.row(InlineKeyboardButton("✅ Verify Subscription", callback_data="verificar"))
            texto = "🔒 **Download Locked**\n\nTo download this APK, please join the required channel below.\n\nAfter joining, press **Verify Subscription**."
            bot.send_message(user_id, texto, reply_markup=markup, parse_mode="Markdown")
    else:
        exibir_menu(message)

@bot.message_handler(commands=['menu'])
def exibir_menu(message):
    texto = "✅ **Subscription Verified**\n\n📦 **Escolha a sua versão do WhatsApp:**"
    bot.send_message(message.chat.id, texto, reply_markup=menu_apks(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "verificar")
def verificar_clique(call):
    user_id = call.from_user.id
    if checar_inscricao(user_id):
        id_msg = downloads_pendentes.get(user_id)
        if id_msg:
            bot.answer_callback_query(call.id, "Inscrição confirmada! Enviando...")
            try:
                bot.edit_message_text("✅ Autorizado! Enviando o arquivo...", chat_id=user_id, message_id=call.message.message_id)
                bot.copy_message(user_id, CANAL_BANCO_DADOS, int(id_msg))
                downloads_pendentes.pop(user_id, None)
            except Exception as e:
                print(f"Erro verificar: {e}")
                bot.send_message(user_id, "❌ Erro ao enviar o arquivo.")
        else:
            bot.answer_callback_query(call.id, "Inscrição confirmada!")
            bot.edit_message_text("✅ Autorizado! Escolha seu APK abaixo:", chat_id=user_id, message_id=call.message.message_id, reply_markup=menu_apks())
    else:
        bot.answer_callback_query(call.id, "❌ Você ainda não entrou no canal!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("apk_"))
def processar_escolha_apk(call):
    mapeamento_ids = {"apk_bmwa_gb": 18, "apk_bmwa_gb_amoled": 19, "apk_bmwa_wa": 20, "apk_bmwa_wa_amoled": 21}
    id_msg = mapeamento_ids.get(call.data)
    if id_msg:
        if not checar_inscricao(call.from_user.id):
            bot.answer_callback_query(call.id, "❌ Você precisa entrar no canal primeiro!", show_alert=True)
            return
        try:
            bot.answer_callback_query(call.id, "Enviando APK...")
            bot.copy_message(call.from_user.id, CANAL_BANCO_DADOS, int(id_msg))
        except Exception as e:
            print(f"Erro apk: {e}")
            bot.answer_callback_query(call.id, "❌ Erro: o Bot precisa ser ADMIN do canal privado!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "refresh_menu")
def recarregar_menu(call):
    bot.answer_callback_query(call.id, "Menu atualizado!")
    texto = "✅ **Subscription Verified**\n\n📦 **Escolha a sua versão do WhatsApp:**"
    bot.edit_message_text(texto, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=menu_apks(), parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.chat.id == DONO_ID, content_types=['document', 'video', 'audio'])
def salvar_arquivo_dono(message):
    try:
        msg_copiada = bot.copy_message(CANAL_BANCO_DADOS, DONO_ID, message.message_id)
        id_da_msg_salva = msg_copiada.message_id
        bot_info = bot.get_me()
        link_download = f"https://t.me/{bot_info.username}?start={id_da_msg_salva}"
        bot.reply_to(message, f"✅ **Arquivo salvo no banco de dados!**\n\nID da mensagem: `{id_da_msg_salva}`\n\nLink direto:\n{link_download}", parse_mode="Markdown")
    except Exception as e:
        print(f"Erro salvar: {e}")
        bot.reply_to(message, "❌ Erro ao salvar no Banco de Dados. Verifique se o Bot é ADMIN do canal privado.")

print("🤖 Bot iniciado! Aguardando mensagens...")
bot.infinity_polling(skip_pending=True)
    

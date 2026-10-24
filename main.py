import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ============================================================
# CONFIGURAÇÕES
# ============================================================

TOKEN = '8988527445:AAFHWFcGDtYZ1I7iqf2XmcQv6XxQY98twEM'

bot = telebot.TeleBot(TOKEN)

DONO_ID = 7599067084

CANAL_BANCO_DADOS = -1004358687748

CANAL_OBRIGATORIO = '@lcmodsrepoo'


# Dicionário temporário para salvar requisições
downloads_pendentes = {}


# ============================================================
# VERIFICAR INSCRIÇÃO NO CANAL
# ============================================================

def checar_inscricao(user_id):
    """Verifica se o usuário está inscrito no canal obrigatório."""

    try:
        status = bot.get_chat_member(
            CANAL_OBRIGATORIO,
            user_id
        ).status

        return status in [
            'member',
            'administrator',
            'creator'
        ]

    except Exception:
        return False


# ============================================================
# MENU DOS APKS
# ============================================================

def menu_apks():
    """Gera o menu com os 4 APKs."""

    markup = InlineKeyboardMarkup()

    # Linha 1
    markup.row(
        InlineKeyboardButton(
            "📦 BMWA_GB",
            callback_data="apk_bmwa_gb"
        ),
        InlineKeyboardButton(
            "📦 BMWA_WA",
            callback_data="apk_bmwa_wa"
        )
    )

    # Linha 2
    markup.row(
        InlineKeyboardButton(
            "🖤 BMWA_GB_AMOLED",
            callback_data="apk_bmwa_gb_amoled"
        ),
        InlineKeyboardButton(
            "🖤 BMWA_WA_AMOLED",
            callback_data="apk_bmwa_wa_amoled"
        )
    )

    # Linha 3
    markup.row(
        InlineKeyboardButton(
            "🔄 Refresh",
            callback_data="refresh_menu"
        )
    )

    return markup


# ============================================================
# COMANDO /START
# ============================================================

@bot.message_handler(commands=['start'])
def start_cmd(message):

    args = message.text.split()

    user_id = message.chat.id

    # --------------------------------------------------------
    # /start COM PARÂMETRO
    # --------------------------------------------------------

    if len(args) > 1:

        id_mensagem_apk = args[1]

        downloads_pendentes[user_id] = id_mensagem_apk

        # Verifica inscrição
        if checar_inscricao(user_id):

            bot.send_message(
                user_id,
                "⌛ Enviando o seu APK, aguarde..."
            )

            try:

                bot.copy_message(
                    user_id,
                    CANAL_BANCO_DADOS,
                    int(id_mensagem_apk)
                )

            except Exception:

                bot.send_message(
                    user_id,
                    "❌ Erro ao enviar arquivo. "
                    "Verifique se o Bot é ADM do canal privado."
                )

        else:

            markup = InlineKeyboardMarkup()

            markup.row(
                InlineKeyboardButton(
                    "➕ Entrar no Canal",
                    url="https://t.me/"
                    + CANAL_OBRIGATORIO.replace('@', '')
                )
            )

            markup.row(
                InlineKeyboardButton(
                    "✅ Verify Subscription",
                    callback_data="verificar"
                )
            )

            texto = (
                "🔒 **Download Locked**\n\n"
                "To download this APK, please join "
                "the required channel below.\n\n"
                "After joining, press **Verify Subscription**."
            )

            bot.send_message(
                user_id,
                texto,
                reply_markup=markup,
                parse_mode="Markdown"
            )

    # --------------------------------------------------------
    # /START SEM PARÂMETRO
    # --------------------------------------------------------

    else:

        exibir_menu(message)


# ============================================================
# COMANDO /MENU
# ============================================================

@bot.message_handler(commands=['menu'])
def exibir_menu(message):

    texto = (
        "✅ **Subscription Verified**\n\n"
        "📦 **Escolha a sua versão do WhatsApp:**"
    )

    bot.send_message(
        message.chat.id,
        texto,
        reply_markup=menu_apks(),
        parse_mode="Markdown"
    )


# ============================================================
# BOTÃO VERIFY SUBSCRIPTION
# ============================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "verificar"
)
def verificar_clique(call):

    user_id = call.from_user.id

    # Verifica novamente
    if checar_inscricao(user_id):

        id_msg = downloads_pendentes.get(user_id)

        # ----------------------------------------------------
        # Usuário veio através de link de download
        # ----------------------------------------------------

        if id_msg:

            bot.answer_callback_query(
                call.id,
                "Inscrição confirmada! Enviando..."
            )

            try:

                bot.edit_message_text(
                    "✅ Autorizado! Enviando o arquivo...",
                    chat_id=user_id,
                    message_id=call.message.message_id
                )

                bot.copy_message(
                    user_id,
                    CANAL_BANCO_DADOS,
                    int(id_msg)
                )

                # Remove a requisição temporária
                downloads_pendentes.pop(user_id, None)

            except Exception:

                bot.send_message(
                    user_id,
                    "❌ Erro ao enviar o arquivo."
                )

        # ----------------------------------------------------
        # Usuário apenas verificou a inscrição
        # ----------------------------------------------------

        else:

            bot.answer_callback_query(
                call.id,
                "Inscrição confirmada!"
            )

            bot.edit_message_text(
                "✅ Autorizado! Escolha seu APK abaixo:",
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=menu_apks()
            )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Você ainda não entrou no canal!",
            show_alert=True
        )


# ============================================================
# ESCOLHA DO APK
# ============================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("apk_")
)
def processar_escolha_apk(call):

    # IDs das mensagens no canal privado
    mapeamento_ids = {

        "apk_bmwa_gb": 18,

        "apk_bmwa_gb_amoled": 19,

        "apk_bmwa_wa": 20,

        "apk_bmwa_wa_amoled": 21

    }

    id_msg = mapeamento_ids.get(call.data)

    if id_msg:

        # Verifica inscrição antes de enviar
        if not checar_inscricao(call.from_user.id):

            bot.answer_callback_query(
                call.id,
                "❌ Você precisa entrar no canal primeiro!",
                show_alert=True
            )

            return

        try:

            bot.answer_callback_query(
                call.id,
                "Enviando APK..."
            )

            bot.copy_message(
                call.from_user.id,
                CANAL_BANCO_DADOS,
                int(id_msg)
            )

        except Exception:

            bot.answer_callback_query(
                call.id,
                "❌ Erro: o Bot precisa ser ADMIN do canal privado!",
                show_alert=True
            )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ ID não configurado no código.",
            show_alert=True
        )


# ============================================================
# BOTÃO REFRESH
# ============================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "refresh_menu"
)
def recarregar_menu(call):

    bot.answer_callback_query(
        call.id,
        "Menu atualizado!"
    )

    texto = (
        "✅ **Subscription Verified**\n\n"
        "📦 **Escolha a sua versão do WhatsApp:**"
    )

    bot.edit_message_text(
        texto,
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=menu_apks(),
        parse_mode="Markdown"
    )


# ============================================================
# RECEBER ARQUIVOS DO DONO
# ============================================================

@bot.message_handler(
    func=lambda msg: msg.chat.id == DONO_ID,
    content_types=[
        'document',
        'video',
        'audio'
    ]
)
def salvar_arquivo_dono(message):

    try:

        # Copia o arquivo para o canal de banco de dados
        msg_copiada = bot.copy_message(
            CANAL_BANCO_DADOS,
            DONO_ID,
            message.message_id
        )

        id_da_msg_salva = msg_copiada.message_id

        # Pega o username do bot
        bot_info = bot.get_me()

        # Cria o link de download
        link_download = (
            f"https://t.me/{bot_info.username}"
            f"?start={id_da_msg_salva}"
        )

        bot.reply_to(
            message,
            (
                "✅ **Arquivo salvo no banco de dados!**\n\n"
                f"ID da mensagem: `{id_da_msg_salva}`\n\n"
                "Link direto:\n"
                f"{link_download}"
            ),
            parse_mode="Markdown"
        )

    except Exception:

        bot.reply_to(
            message,
            (
                "❌ Erro ao salvar no Banco de Dados.\n\n"
                "Verifique se o Bot é ADMIN do canal privado."
            )
        )


# ============================================================
# INICIAR BOT
# ============================================================

print("🤖 Bot iniciado!")

bot.infinity_polling()

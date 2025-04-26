import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Pegando o token do ambiente Railway
TOKEN = os.getenv("BOT_TOKEN")

# Agora usando dicionário {user_id: (username, first_name)}
participants = {}

# Para armazenar o ID da mensagem principal e o ID do chat
message_id_store = {"chat_id": None, "message_id": None}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎉 Participar", callback_data="join_raffle")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Envia a mensagem inicial e salva o ID dela
    sent_message = await update.message.reply_text(
        f"🎉 Sorteio Aberto! 🎉\n"
        f"Já temos 0 participando!\n"
        f"Clique no botão Participar para entrar! 🚀\n"
        f"📎 Cadastre-se também aqui: https://bit.ly/42puLF6\n"
        f"Boa sorte! 🍀",
        reply_markup=reply_markup
    )

    # Salva o chat_id e o message_id para futuras edições
    message_id_store["chat_id"] = sent_message.chat.id
    message_id_store["message_id"] = sent_message.message_id

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "join_raffle":
        user = query.from_user
        participants[user.id] = (user.username, user.first_name)

        # Atualizar a mensagem com o novo número de participantes
        try:
            await context.bot.edit_message_text(
                chat_id=message_id_store["chat_id"],
                message_id=message_id_store["message_id"],
                text=(
                    f"🎉 Sorteio Aberto! 🎉\n"
                    f"Já temos {len(participants)} participando!\n"
                    f"Clique no botão Participar para entrar! 🚀\n"
                    f"📎 Cadastre-se também aqui: https://bit.ly/42puLF6\n"
                    f"Boa sorte! 🍀"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🎉 Participar", callback_data="join_raffle")]]
                )
            )
        except Exception as e:
            logging.error(f"Erro ao editar a mensagem: {e}")

async def raffle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not participants:
        await update.message.reply_text("Nenhum participante registrado ainda.")
        return

    winners_count = 5  # Número de ganhadores
    winners = random.sample(list(participants.keys()), min(winners_count, len(participants)))

    winners_text = 'OS GANHADORES DAS BANCAS SÃO 🎉🔥:\n\n'

    for winner_id in winners:
        username, first_name = participants[winner_id]
        if username:
            winners_text += f"@{username}, "
        else:
            winners_text += f"[{first_name}](tg://user?id={winner_id}), "

    winners_text = winners_text.rstrip(", ")  # Remove a última vírgula
    winners_text += f"\n\nO número de participantes neste sorteio foi {len(participants)} pessoas 🌎"

    await update.message.reply_text(winners_text, parse_mode='Markdown')

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("raffle", raffle))

    app.run_polling()

if __name__ == '__main__':
    main()

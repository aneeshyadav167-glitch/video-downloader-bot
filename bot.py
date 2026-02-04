import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Link bhejo, video Telegram format me milega."
    )


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    await update.message.reply_text("⏳ Processing...")

    ydl_opts = {
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
    }

    os.makedirs("downloads", exist_ok=True)

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        size = os.path.getsize(file) / (1024 * 1024)
        size = round(size, 2)

        caption = f"📦 Size: {size} MB"

        await update.message.reply_video(
            video=open(file, "rb"),
            caption=caption,
            supports_streaming=True
        )

        os.remove(file)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Ye link supported nahi hai.")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

    app.run_polling()


if __name__ == "__main__":
    main()
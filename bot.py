import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi!\nKoi bhi public video ya TeraBox link bhejo."
    )


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    await update.message.reply_text("⏳ Download start ho gaya...")


    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file, 'rb'))

        os.remove(file)

    except:
        await update.message.reply_text("❌ Ye link supported nahi hai.")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

    app.run_polling()


if __name__ == "__main__":
    main()

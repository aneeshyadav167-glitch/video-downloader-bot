import os
import re
import requests
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")


# Expand short / redirect links
def expand_url(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url


# Check if TeraBox link
def is_terabox(url):
    return "terabox" in url or "1024tera" in url


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi!\nKoi bhi public video ya TeraBox link bhejo."
    )


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    await update.message.reply_text("⏳ Download start ho gaya...")

    # Expand redirect
    url = expand_url(url)

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    os.makedirs("downloads", exist_ok=True)

    try:

        # For TeraBox
        if is_terabox(url):
            ydl_opts["extractor_args"] = {
                "terabox": {
                    "api": ["https://www.1024tera.com"]
                }
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file, 'rb'))

        os.remove(file)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Ye link supported nahi hai ya private hai.")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

    print("Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
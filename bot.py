import os
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Link bhejo, quality choose karo (Original bhi milega)."
    )


# Step 1: Get formats
async def get_formats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()
    context.user_data["url"] = url

    await update.message.reply_text("🔍 Checking qualities...")

    ydl_opts = {"quiet": True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])

        buttons = []

        used = set()

        # Original / Best button
        buttons.append([
            InlineKeyboardButton("🔥 Original (Best)", callback_data="best")
        ])

        for f in formats:
            if f.get("vcodec") != "none" and f.get("height"):
                q = f"{f['height']}p"

                if q not in used:
                    used.add(q)
                    buttons.append(
                        [InlineKeyboardButton(q, callback_data=q)]
                    )

        if len(buttons) == 1:
            await update.message.reply_text("❌ Quality nahi mili.")
            return

        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
            "📽️ Quality select karo:",
            reply_markup=reply_markup
        )

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Link supported nahi hai.")


# Step 2: Download selected quality
async def download_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    choice = query.data
    url = context.user_data.get("url")

    await query.edit_message_text(f"⏳ Downloading {choice}...")

    if choice == "best":
        fmt = "bestvideo+bestaudio/best"
    else:
        height = choice.replace("p", "")
        fmt = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

    ydl_opts = {
        "format": fmt,
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True,
        "merge_output_format": "mp4"
    }

    os.makedirs("downloads", exist_ok=True)

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await query.message.reply_video(
            open(file, "rb"),
            supports_streaming=True
        )

        os.remove(file)

    except Exception as e:
        print(e)
        await query.message.reply_text("❌ Download failed.")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_formats))
    app.add_handler(CallbackQueryHandler(download_selected))

    app.run_polling()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Zbr10 Social Manager Bot
Telegram se apne Facebook/Instagram pages manage karo.

SETUP:
  1. pip install python-telegram-bot requests
  2. Apna naya bot token env var me rakho:
       Windows: set TELEGRAM_BOT_TOKEN=apna_token_yahan
       Linux/Mac: export TELEGRAM_BOT_TOKEN=apna_token_yahan
  3. python bot.py

Page ka access token Meta ke Graph API Explorer se lo (sirf apne pages ka).
Ye token pages.json me save hota hai — SIRF tumhare computer pe rehta hai.
"""

import json
import logging
import os

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

PAGES_FILE = "pages.json"
GRAPH = "https://graph.facebook.com/v21.0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_pages():
    if os.path.exists(PAGES_FILE):
        with open(PAGES_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_pages(pages):
    with open(PAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalam-o-Alaikum! 🤖 Main tumhara Social Manager Bot hoon.\n\n"
        "Commands:\n"
        "/addpage <naam> <page_id> <token> — naya page connect karo\n"
        "/pages — connected pages dekho\n"
        "/delpage <naam> — page hatao\n"
        "/post <naam> <text> — page pe post karo\n"
        "/pageinfo <naam> — page ki info dekho\n"
        "/help — ye list dobara dekho"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def addpage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text(
            "Tareeqa: /addpage <naam> <page_id> <page_access_token>\n"
            "Misaal: /addpage myshop 123456789 ABCtokenXYZ"
        )
        return
    name, page_id, token = context.args[0], context.args[1], context.args[2]
    pages = load_pages()
    pages[name] = {"page_id": page_id, "token": token}
    save_pages(pages)
    await update.message.reply_text(f"✅ Page '{name}' connect ho gaya!")


async def listpages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pages = load_pages()
    if not pages:
        await update.message.reply_text("Koi page connect nahi hai. /addpage se joro.")
        return
    await update.message.reply_text(
        "Connected pages:\n" + "\n".join(f"• {n} (id: {p['page_id']})" for n, p in pages.items())
    )


async def delpage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Tareeqa: /delpage <naam>")
        return
    pages = load_pages()
    name = context.args[0]
    if name in pages:
        del pages[name]
        save_pages(pages)
        await update.message.reply_text(f"🗑 Page '{name}' hata diya.")
    else:
        await update.message.reply_text(f"'{name}' naam ka page nahi mila.")


async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Tareeqa: /post <naam> <tumhara text>")
        return
    name = context.args[0]
    text = " ".join(context.args[1:])
    pages = load_pages()
    if name not in pages:
        await update.message.reply_text(f"'{name}' connect nahi hai. Pehle /addpage karo.")
        return
    p = pages[name]
    try:
        r = requests.post(
            f"{GRAPH}/{p['page_id']}/feed",
            data={"message": text, "access_token": p["token"]},
            timeout=20,
        )
        data = r.json()
        if "id" in data:
            await update.message.reply_text(f"✅ Post ho gaya! (post id: {data['id']})")
        else:
            await update.message.reply_text(f"❌ Error: {data.get('error', {}).get('message', data)}")
    except Exception as e:
        logger.exception("post failed")
        await update.message.reply_text(f"❌ Masla hua: {e}")


async def pageinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Tareeqa: /pageinfo <naam>")
        return
    name = context.args[0]
    pages = load_pages()
    if name not in pages:
        await update.message.reply_text(f"'{name}' connect nahi hai.")
        return
    p = pages[name]
    try:
        r = requests.get(
            f"{GRAPH}/{p['page_id']}",
            params={"fields": "name,followers_count,fan_count", "access_token": p["token"]},
            timeout=20,
        )
        d = r.json()
        if "error" in d:
            await update.message.reply_text(f"❌ Error: {d['error'].get('message')}")
        else:
            await update.message.reply_text(
                f"📄 {d.get('name')}\nFollowers: {d.get('followers_count', d.get('fan_count', '?'))}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Masla hua: {e}")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN env var set karo, phir dobara chalao.")
    proxy = os.environ.get("TELEGRAM_PROXY")  # optional, e.g. socks5://user:pass@host:port
    builder = ApplicationBuilder().token(token)
    if proxy:
        builder = builder.proxy(proxy)
        logger.info("Proxy use ho raha hai.")
    app = builder.build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("addpage", addpage))
    app.add_handler(CommandHandler("pages", listpages))
    app.add_handler(CommandHandler("delpage", delpage))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("pageinfo", pageinfo))
    logger.info("Bot chal raha hai...")
    webhook_url = os.environ.get("WEBHOOK_URL")  # e.g. https://mybot.onrender.com (Render pe)
    if webhook_url:
        # Webhook mode (Render/server): Telegram khud hamare URL pe message bhejega
        port = int(os.environ.get("PORT", "8443"))
        logger.info(f"Webhook mode: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=f"{webhook_url}/{token}",
        )
    else:
        # Polling mode (apne laptop/PC pe)
        app.run_polling()


if __name__ == "__main__":
    main()

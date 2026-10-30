# Zbr10 Social Manager Bot — Setup (5 minute)

## 1. Python install karo (agar nahi hai)
python.org se Python 3.10+ install karo. Phir:
```
pip install python-telegram-bot requests
```

## 2. Apna NAYA token env var me rakho (chat me kabhi mat bhejo)
Windows (CMD):
```
set TELEGRAM_BOT_TOKEN=apna_naya_token_yahan
```
Linux/Mac:
```
export TELEGRAM_BOT_TOKEN=apna_naya_token_yahan
```

## 3. Bot chalao
```
python bot.py
```
Telegram me apne bot ko `/start` bhejo.

## 4. Facebook page connect karo
- developers.facebook.com → apna app → Graph API Explorer
- Apne page ka **Page Access Token** lo (sirf apne pages ka!)
- Bot me bhejo: `/addpage myshop PAGE_ID TOKEN`
- Post karo: `/post myshop Assalam-o-Alaikum! Ye meri pehli bot post hai.`

## Notes
- `pages.json` sirf tumhare computer pe banta hai — tokens kahin aur nahi jate.
- TikTok: sirf business accounts official API se jurte hain — wo step 2 me ayega.
- Kisi aur ka account ya fake accounts is me mat jorna — wahi legal line hai.

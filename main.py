from fastapi import FastAPI, Request
import os, random, json
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API=f'https://api.telegram.org/bot{BOT_TOKEN}'

app = FastAPI()

with open("db.json") as db:
	anime_db = json.load(db)

@app.post("/webhook")
async def telegram_webhook(req: Request):
	req_body = await req.json()
	# Handle normal message
	if "message" in req_body:
		msg = req_body["message"]
		chat_id= msg["chat"]["id"]
		text = msg.get("text", "")
		if text == "/start":
			await send_genre_buttons(chat_id)
		else:
			await send_message(chat_id=chat_id, text="Type /Start to get anime recommendations...")
	# Handle callback query
	elif "callback_query" in req_body:
		data = req_body["callback_query"]["data"]
		chat_id = req_body["callback_query"]["message"]['chat']['id']
		genre = data.replace("genre_", "")

		if genre in anime_db:
			anime = random.choice(anime_db[genre])
			reply = f"{emoji(genre)} Try: {anime}"
		else:
			reply="Sorry genre's too unique"
		
		await send_message(chat_id, reply)
	
	return {"ok": True}


async def send_genre_buttons(chat_id):
	inline_keyboard = {
		"inline_keyboard": [
			[{"text": "Romance", "callback_data": "romance"}],
			[{"text": "Isekai", "callback_data": "isekai"}]
		]
	}
	async with httpx.AsyncClient() as client:
		await client.post(f"{TELEGRAM_API}/sendMessage", json={
			"chat_id": chat_id,
			"text": "Choose a genre 🎭:",
			"reply_markup": inline_keyboard
		})

async def send_message(chat_id, text):
	async with httpx.AsyncClient() as client:
		await client.post(f"{TELEGRAM_API}/sendMessage", json={
			"chat_id": chat_id,
			"text": text
		})

def emoji(genre):
	return {
		"romance": "💖",
        	"isekai": "🌌"
	}.get(genre, "🎬")

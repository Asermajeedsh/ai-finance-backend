from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

openai.api_key = os.getenv("OPENAI_API_KEY")
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def fetch_stock(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_KEY
    }
    r = requests.get(url).json()

    if "Global Quote" not in r or not r["Global Quote"]:
        raise HTTPException(status_code=400, detail="Invalid stock symbol or API limit reached")

    quote = r["Global Quote"]
    price = quote.get("05. price", "0")
    change = quote.get("10. change percent", "0%")
    return float(price), change

def fetch_crypto(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    r = requests.get(url).json()
    return r.get(symbol, {}).get("usd", 0)

def ai_insight(asset, change):
    prompt = f"The price of {asset} changed {change}. Give a short investment insight in simple language."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    return response.choices[0].message.content

@app.get("/")
def home():
    return {"message": "Velaris AI backend is live"}

@app.get("/stock/{symbol}")
def stock(symbol: str):
    try:
        price, change = fetch_stock(symbol)
        insight = ai_insight(symbol, change)
        return {"symbol": symbol, "price": price, "change": change, "insight": insight}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crypto/{symbol}")
def crypto(symbol: str):
    try:
        price = fetch_crypto(symbol)
        insight = ai_insight(symbol, "today")
        return {"symbol": symbol, "price": price, "insight": insight}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

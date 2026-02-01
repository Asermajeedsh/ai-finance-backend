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
    # Try Alpha Vantage first
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_KEY
    }
    r = requests.get(url).json()

    quote = r.get("Global Quote")
    if quote and "05. price" in quote:
        price = quote.get("05. price")
        change = quote.get("10. change percent", "0%")
        return float(price), change

    # Fallback: Yahoo Finance unofficial API
    yahoo_url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    y = requests.get(yahoo_url).json()
    result = y.get("quoteResponse", {}).get("result", [])

    if not result:
        raise HTTPException(status_code=400, detail="Invalid stock symbol or data unavailable")

    stock = result[0]
    price = stock.get("regularMarketPrice", 0)
    change = stock.get("regularMarketChangePercent", 0)
    change_str = f"{change:.2f}%" if isinstance(change, (int, float)) else "0%"

    return float(price), change_str

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
    price, change = fetch_stock(symbol)
    insight = ai_insight(symbol, change)
    return {"symbol": symbol, "price": price, "change": change, "insight": insight}

@app.get("/crypto/{symbol}")
def crypto(symbol: str):
    price = fetch_crypto(symbol)
    insight = ai_insight(symbol, "today")
    return {"symbol": symbol, "price": price, "insight": insight}

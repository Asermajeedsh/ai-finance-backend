from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def safe_json(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def fetch_stock(symbol):
    # Try Alpha Vantage
    alpha_data = safe_json("https://www.alphavantage.co/query", {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_KEY
    })

    if alpha_data:
        quote = alpha_data.get("Global Quote")
        if quote and "05. price" in quote:
            try:
                price = float(quote.get("05. price"))
                change = quote.get("10. change percent", "0%")
                return price, change
            except:
                pass

    # Fallback: Yahoo Finance
    yahoo_data = safe_json("https://query1.finance.yahoo.com/v7/finance/quote", {
        "symbols": symbol
    })

    if yahoo_data:
        results = yahoo_data.get("quoteResponse", {}).get("result", [])
        if results:
            stock = results[0]
            price = stock.get("regularMarketPrice", 0)
            change = stock.get("regularMarketChangePercent", 0)
            try:
                price = float(price)
                change_str = f"{float(change):.2f}%"
            except:
                change_str = "0%"
            return price, change_str

    # Final fallback
    return 0.0, "0%"

def fetch_crypto(symbol):
    data = safe_json("https://api.coingecko.com/api/v3/simple/price", {
        "ids": symbol,
        "vs_currencies": "usd"
    })

    if data and symbol in data and "usd" in data[symbol]:
        try:
            return float(data[symbol]["usd"])
        except:
            pass

    return 0.0

def ai_insight(asset, change):
    prompt = f"The price of {asset} changed {change}. Give a short investment insight in simple language."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import openai
import stripe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

openai.api_key = ""

stripe.api_key = ""

def fetch_stock(symbol):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey="
    r = requests.get(url).json()
    price = r["Global Quote"]["05. price"]
    change = r["Global Quote"]["10. change percent"]
    return float(price), change

def fetch_crypto(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    r = requests.get(url).json()
    return r[symbol]["usd"]

def ai_insight(asset, change):
    prompt = f"The price of {asset} changed {change}. Give a short investment insight."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60
    )
    return response.choices[0].message.content

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

@app.post("/checkout")
def checkout(email: str):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": "PRICE_ID_HERE", "quantity": 1}],
        success_url="https://yourfrontend.com/success",
        cancel_url="https://yourfrontend.com/cancel",
        customer_email=email
    )
    return {"url": session.url}

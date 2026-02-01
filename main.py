from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def home():
    return {"message": "Velaris backend is live and stable"}

@app.get("/stock/{symbol}")
def stock(symbol: str):
    price = round(random.uniform(50, 500), 2)
    change = f"{round(random.uniform(-5, 5), 2)}%"
    insight = ai_insight(symbol, change)
    return {"symbol": symbol, "price": price, "change": change, "insight": insight}

@app.get("/crypto/{symbol}")
def crypto(symbol: str):
    price = round(random.uniform(1000, 50000), 2)
    insight = ai_insight(symbol, "today")
    return {"symbol": symbol, "price": price, "insight": insight}

def ai_insight(asset, change):
    prompt = f"The price of {asset} changed {change}. Give a short investment insight in simple language."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    return response.choices[0].message.content

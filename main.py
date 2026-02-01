from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Demo stock & crypto data
STOCKS = {
    "TSLA": {"price": 185.32, "change": "1.23%", "insight": "Tesla stock is slightly up today; investors remain optimistic."},
    "AAPL": {"price": 145.67, "change": "-0.85%", "insight": "Apple dipped slightly; market sentiment is cautious."}
}

CRYPTOS = {
    "bitcoin": {"price": 43000, "insight": "Bitcoin remains volatile today; traders are watching closely."},
    "ethereum": {"price": 3200, "insight": "Ethereum shows steady growth; investor confidence is moderate."}
}

@app.get("/")
def home():
    return {"message": "Velaris AI backend is live"}

@app.get("/stock/{symbol}")
def stock(symbol: str):
    data = STOCKS.get(symbol.upper())
    if not data:
        return {"symbol": symbol, "price": 0, "change": "0%", "insight": "No data available."}
    return {"symbol": symbol, **data}

@app.get("/crypto/{symbol}")
def crypto(symbol: str):
    # Case-insensitive lookup
    key = symbol.lower()
    data = CRYPTOS.get(key)
    if not data:
        return {"symbol": symbol, "price": 0, "insight": "No data available."}
    return {"symbol": symbol, **data}

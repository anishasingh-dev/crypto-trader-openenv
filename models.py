from __future__ import annotations
from typing import Literal, Dict, List
from pydantic import BaseModel, Field

CRYPTOS = ["BTC","ETH","XRP","ADA","SOL"]
Decision = Literal["BUY","SELL","HOLD"]

class CryptoAction(BaseModel):
    ticker: str = Field("BTC", description="Which crypto to trade")
    decision: Decision = Field("HOLD", description="BUY, SELL, or HOLD")
    quantity: int = Field(1, ge=1, le=10, description="Number of units")

class Candle(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class CryptoObservation(BaseModel):
    step: int
    max_steps: int
    done: bool
    cash: float
    holdings: Dict[str,int]
    prices: Dict[str,float]
    candles: Dict[str,List[Candle]]
    sentiment: Dict[str,float]
    portfolio_value: float
    pnl_pct: float

class CryptoState(BaseModel):
    step: int
    done: bool
    cash: float
    holdings: Dict[str,int]
    portfolio_value: float
    pnl_pct: float
    total_trades: int

class StepResult(BaseModel):
    observation: CryptoObservation
    reward: float
    done: bool
    info: dict
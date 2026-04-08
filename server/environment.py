from __future__ import annotations
import random, math
from datetime import datetime, timedelta
from typing import Dict, List
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import CryptoAction, CryptoObservation, CryptoState, StepResult, Candle, CRYPTOS

STARTING_CASH = 5000.0
MAX_STEPS = 20
LOOKBACK = 20

def _generate_price_series(ticker: str, days: int) -> List[Dict]:
    random.seed(hash(ticker) % 9999)
    base = {"BTC": 30000, "ETH": 2000, "XRP": 0.7, "ADA": 0.35, "SOL": 22}[ticker]
    price = float(base)
    series = []
    start = datetime(2024,1,1)
    for i in range(days):
        change = random.gauss(0.002,0.03)
        price *= (1+change)
        high = price * (1 + abs(random.gauss(0,0.01)))
        low = price * (1 - abs(random.gauss(0,0.01)))
        volume = int(random.uniform(1000, 50000))
        series.append({
            "date": (start+timedelta(days=i)).strftime("%Y-%m-%d"),
            "open": round(price*random.uniform(0.998,1.002),2),
            "high": round(high,2),
            "low": round(low,2),
            "close": round(price,2),
            "volume": volume,
        })
    return series

def _sentiment(ticker: str, day: int) -> float:
    random.seed(hash(ticker+str(day)) % 99999)
    return round(random.uniform(-1,1),3)

class CryptoTradingEnvironment:
    def __init__(self):
        self._price_history: Dict[str,List[Dict]] = {}
        self._step = 0
        self._done = False
        self._cash = STARTING_CASH
        self._holdings: Dict[str,int] = {t:0 for t in CRYPTOS}
        self._trades: List[dict] = []

    def reset(self) -> CryptoObservation:
        self._price_history = {t:_generate_price_series(t, MAX_STEPS+LOOKBACK) for t in CRYPTOS}
        self._step = 0
        self._done = False
        self._cash = STARTING_CASH
        self._holdings = {t:0 for t in CRYPTOS}
        self._trades = []
        return self._build_obs()

    def step(self, action: CryptoAction) -> StepResult:
        if self._done:
            raise RuntimeError("Episode finished — call reset() first.")
        current_step = self._step
        price = self._price_at(action.ticker, current_step)
        prev_value = self._portfolio_value(current_step)
        info = {"ticker": action.ticker, "decision": action.decision, "quantity": action.quantity, "price": price, "step": current_step}
        if action.decision=="BUY":
            cost = price*action.quantity
            if cost <= self._cash:
                self._cash -= cost
                self._holdings[action.ticker] += action.quantity
                info["executed"]=True
            else:
                info["executed"]=False
                info["reason"]="insufficient_cash"
        elif action.decision=="SELL":
            if self._holdings[action.ticker] >= action.quantity:
                self._cash += price*action.quantity
                self._holdings[action.ticker] -= action.quantity
                info["executed"]=True
            else:
                info["executed"]=False
                info["reason"]="insufficient_holdings"
        else:
            info["executed"]=True
        self._trades.append(info)
        self._step += 1
        if self._step>=MAX_STEPS: self._done=True
        obs = self._build_obs()
        reward = round(self._portfolio_value(self._step-1)-prev_value,4)
        return StepResult(observation=obs, reward=reward, done=self._done, info=info)

    @property
    def state(self) -> CryptoState:
        return CryptoState(
            step=self._step,
            done=self._done,
            cash=round(self._cash,2),
            holdings=self._holdings,
            portfolio_value=round(self._portfolio_value(self._step),2),
            pnl_pct=round((self._portfolio_value(self._step)/STARTING_CASH-1)*100,3),
            total_trades=len(self._trades),
        )

    def _price_at(self, ticker: str, step: int) -> float:
        return self._price_history[ticker][step+LOOKBACK-1]["close"]

    def _portfolio_value(self, step: int) -> float:
        cash = self._cash
        for t in CRYPTOS:
            cash += self._price_at(t,step)*self._holdings[t]
        return cash

    def _build_obs(self) -> CryptoObservation:
        s = self._step
        prices_today = {t:self._price_at(t,s) for t in CRYPTOS}
        portfolio = self._cash + sum(prices_today[t]*self._holdings[t] for t in CRYPTOS)
        candles: Dict[str,list] = {}
        for t in CRYPTOS:
            window = self._price_history[t][s+LOOKBACK-5:s+LOOKBACK]
            candles[t] = [Candle(**c) for c in window]
        return CryptoObservation(
            step=s,
            max_steps=MAX_STEPS,
            done=self._done,
            cash=round(self._cash,2),
            holdings=self._holdings.copy(),
            prices={t:round(v,2) for t,v in prices_today.items()},
            candles=candles,
            sentiment={t:_sentiment(t,s) for t in CRYPTOS},
            portfolio_value=round(portfolio,2),
            pnl_pct=round((portfolio/STARTING_CASH-1)*100,3),
        )
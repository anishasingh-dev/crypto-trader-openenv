from inference import CryptoTraderClient
from models import CryptoAction

client = CryptoTraderClient()

obs = client.reset()
print(f"Step {obs.step} | Portfolio: {obs.portfolio_value} USD")

# Example: BUY 1 BTC
action = CryptoAction(ticker="BTC", decision="BUY", quantity=1)
result = client.step(action)
print(f"Reward: {result.reward} | Done: {result.done}")
print("Info:", result.info)
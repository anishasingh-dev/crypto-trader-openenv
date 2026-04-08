from __future__ import annotations
import os, json, sys
from typing import Dict
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import CryptoAction, CryptoObservation, StepResult

API_URL = os.getenv("API_URL", "http://localhost:7860")

class CryptoTraderClient:
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id

    def reset(self) -> CryptoObservation:
        resp = requests.post(f"{API_URL}/reset", params={"session_id": self.session_id})
        return CryptoObservation(**resp.json())

    def step(self, action: CryptoAction) -> StepResult:
        resp = requests.post(f"{API_URL}/step", json=action.dict(), params={"session_id": self.session_id})
        return StepResult(**resp.json())

    def state(self) -> Dict:
        resp = requests.get(f"{API_URL}/state", params={"session_id": self.session_id})
        return resp.json()

if __name__ == "__main__":
    client = CryptoTraderClient()
    obs = client.reset()
    print("Reset Observation:", obs)
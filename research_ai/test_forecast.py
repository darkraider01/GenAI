import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import get_forecast
import backend.main as main_module

# Mock trends
mock_trends = [
    {
        "topic_name": "Quantum Machine Learning",
        "growth_rate": 2.5,
        "insight_report": "Rapidly growing area combining quantum computing and machine learning algorithms.",
        "representative_papers": [
            {"title": "Quantum AI Foundation", "url": "http://example.com/paper1.pdf"},
            {"title": "Advancements in QML", "url": "http://example.com/paper2.pdf"}
        ]
    },
    {
        "topic_name": "Federated Learning Privacy",
        "growth_rate": 1.8,
        "insight_report": "Focusing on preserving privacy in distributed machine learning setups.",
        "representative_papers": [
            {"title": "Privacy-Preserving FL", "url": "http://example.com/paper3.pdf"}
        ]
    },
    {
        "topic_name": "Neuromorphic Hardware",
        "growth_rate": 1.2,
        "insight_report": "Hardware architectures inspired by the human brain for low-power AI.",
        "representative_papers": [
            {"title": "Neuromorphic Chips 2025", "url": "http://example.com/paper4.pdf"},
            {"title": "Spiking Neural Networks on Silicon", "url": "http://example.com/paper5.pdf"}
        ]
    }
]

main_module.get_cached_trends = lambda: mock_trends

async def test():
    print("Running forecast test...")
    result = await get_forecast()
    print("\n--- Forecast Result ---")
    print(result.get("forecast", ""))
    print("-----------------------\n")

if __name__ == "__main__":
    asyncio.run(test())

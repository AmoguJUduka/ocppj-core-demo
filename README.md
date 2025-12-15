
# ocppj-core-demo

A minimal **OCPP-J 1.6 (Core profile)** demo using the Mobility House `ocpp` library (`ocpp/v16`).

This project contains:
- **CSMS (Central System)**: WebSocket server that handles BootNotification, Heartbeat, Authorize, StartTransaction, StopTransaction
- **Charge Point (Virtual CP)**: WebSocket client that connects to the CSMS and performs a basic charging session

## Requirements
- Python 3.9+ (tested on Python 3.9)
- Packages: `ocpp`, `websockets`

## Setup
From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt


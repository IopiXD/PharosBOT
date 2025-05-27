# Pharos Daily Bot

## Overview

The Pharos Daily Bot is a Python script designed to automate interactions with the Pharos Network testnet. It helps users complete tasks like sending native tokens, swapping tokens, and adding liquidity to decentralized exchange pools to earn points. The bot comes in two versions: `app.py` (non-proxy) and `appproxy.py` (proxy-enabled for enhanced privacy).

## Register
https://testnet.pharosnetwork.xyz/experience

## Features

- **Task Automation**:
  - Sends small amounts of PHRS to multiple addresses.
  - Swaps PHRS for USDC/USDT and vice versa.
  - Adds liquidity to PHRS/USDC and PHRS/USDT pools.
- **Proxy Support** (appproxy.py): Routes requests through proxies for privacy.
- **Error Handling**: Retries failed API calls and transactions with exponential backoff.
- **Wallet Management**: Processes multiple wallets sequentially with proper nonce handling.
- **Scheduled Runs**: Executes daily at 7:30 AM WIB.
- **Colorful Logging**: Provides clear, timestamped console output.

## Prerequisites

- Python 3.10+
- Private keys for Pharos testnet wallets
- Proxies (for `appproxy.py`)
- Sufficient PHRS for transaction fees

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/IopiXD/PharoBOT.git
   cd PharoBOT
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Files**:
   - **pk.txt**: Add one private key per line:
     ```
     privatekey1
     privatekey2
     ```
   - **proxies.txt** (for `appproxy.py`): Add one proxy per line:
     ```
     http://username:password@ip:port
     http://ip:port
     ```

## Usage

### Non-Proxy Version (app.py)
```bash
python app.py
```

### Proxy Version (appproxy.py)
Ensure `proxies.txt` has enough proxies, then run:
```bash
python appproxy.py
```

The bot will:
- Authenticate wallets, fetch tasks, and display points.
- Perform transactions (send, swap, add liquidity) for each wallet.
- Run 50 iterations per wallet and wait until 7:30 AM WIB for the next cycle.

To stop, press `Ctrl+C`.

## Bot Details

- **Network**: Pharos Network Testnet
- **Tokens**: PHRS, USDC, USDT
- **Tasks**: Send to Friend, Swap, Add Liquidity
- **Schedule**: Daily at 7:30 AM WIB
- **Retries**: Up to 10 with exponential backoff
- **Logging**: Timestamps in Asia/Jakarta timezone

## Beware

- **Security**: Never share your private keys (`pk.txt`) or upload them to GitHub.
- **Testnet Only**: This bot is for the Pharos testnet. Do not use on mainnet.
- **Funds**: Ensure wallets have enough PHRS for gas fees.
- **Proxies**: Use reliable proxies for `appproxy.py` to avoid failures.
- **Legal**: Verify that automating tasks complies with Pharos Network's terms.
- **Risk**: Use at your own risk. The bot interacts with blockchain contracts, and errors may lead to failed transactions.

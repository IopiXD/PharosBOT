import requests
import time
import random
from datetime import datetime, timedelta
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from colorama import init, Fore, Style
import pytz
import os
import builtins
import json
from web3.providers.rpc import HTTPProvider
import uuid

init(autoreset=True)

original_print = builtins.print

def custom_print(*args, **kwargs):
    jakarta_timezone = pytz.timezone('Asia/Jakarta')
    current_time = datetime.now(jakarta_timezone)
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"{Fore.MAGENTA}{time_str} | {Style.RESET_ALL}"
    original_print(prefix, *args, **kwargs)

builtins.print = custom_print

BASE_URL = "https://api.pharosnetwork.xyz"
RPC_URL = "https://testnet.dplabs-internal.com"
TASK_ID = 103
MAX_RETRIES = 10
BACKOFF_FACTOR = 2
WPHRS_CONTRACT_ADDRESS = Web3.to_checksum_address("0x76aaada469d23216be5f7c596fa25f282ff9b364")
USDC_TOKEN = Web3.to_checksum_address("0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED")
USDT_TOKEN = Web3.to_checksum_address("0xD4071393f8716661958F766DF660033b3d35fD29")
ROUTER_ADDRESS = Web3.to_checksum_address("0x1a4de519154ae51200b0ad7c90f7fac75547888a")
NONFUNGIBLE_POSITION_MANAGER_ADDRESS = Web3.to_checksum_address("0xF8a1D4FF0f9b9Af7CE58E1FC1833688F3BFd6115")
QUOTER_ADDRESS = Web3.to_checksum_address("0x00f2f47d1ed593Cf0AF0074173E9DF95afb0206C")
FEE = 500
DEADLINE_MINUTES = 10

WPHRS_ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "amount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

ERC20_ABI = [
    {"inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"internalType": "bytes[]", "name": "data", "type": "bytes[]"}
        ],
        "name": "multicall",
        "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountMinimum", "type": "uint256"},
            {"internalType": "address", "name": "recipient", "type": "address"}
        ],
        "name": "unwrapWETH9",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

NONFUNGIBLE_PM_ABI = [
    {
        "inputs": [{"internalType": "bytes[]", "name": "data", "type": "bytes[]"}],
        "name": "multicall",
        "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "token0", "type": "address"},
                    {"internalType": "address", "name": "token1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickLower", "type": "int24"},
                    {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                    {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "internalType": "struct INonfungiblePositionManager.MintParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "mint",
        "outputs": [
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"}
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "refundETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

QUOTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "internalType": "struct IQuoterV2.QuoteExactInputSingleParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint160", "name": "sqrtPriceX96After", "type": "uint160"},
            {"internalType": "uint32", "name": "initializedTicksCrossed", "type": "uint32"},
            {"internalType": "uint256", "name": "gasEstimate", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

HEADERS_TEMPLATE = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.5',
    'authorization': 'Bearer {}',
    'origin': 'https://testnet.pharosnetwork.xyz',
    'referer': 'https://testnet.pharosnetwork.xyz/',
    'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'content-length': '0'
}

nonce_locks = {}
nonce_cache = {}

def load_proxies():
    try:
        with open("proxies.txt") as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to load proxies: {e}{Style.RESET_ALL}")
        return []

def format_proxy(proxy):
    try:
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            proxy = f'http://{proxy}'
        return proxy
    except Exception as e:
        print(f"{Fore.RED}❌ Invalid proxy format: {e}{Style.RESET_ALL}")
        return None

def get_working_proxy(proxies, used_proxies, max_retries=10):
    available_proxies = [p for p in proxies if p not in used_proxies]
    if not available_proxies:
        print(f"{Fore.RED}❌ No available proxies left{Style.RESET_ALL}")
        return None
    for _ in range(max_retries):
        proxy = random.choice(available_proxies)
        formatted_proxy = format_proxy(proxy)
        if not formatted_proxy:
            continue
        try:
            response = requests.get('https://api.ipify.org', proxies={'http': formatted_proxy, 'https': formatted_proxy}, timeout=10)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ Proxy {proxy} is working{Style.RESET_ALL}")
                return formatted_proxy
            else:
                print(f"{Fore.YELLOW}⚠️ Proxy {proxy} returned status {response.status_code}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Proxy {proxy} failed: {e}{Style.RESET_ALL}")
        available_proxies.remove(proxy)
        if not available_proxies:
            print(f"{Fore.RED}❌ Exhausted all proxies{Style.RESET_ALL}")
            return None
        time.sleep(1)
    print(f"{Fore.RED}❌ No working proxy found after {max_retries} attempts{Style.RESET_ALL}")
    return None

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    banner = """
    ██╗ ██████╗ ██████╗ ██╗
    ██║██╔═══██╗██╔══██╗██║
    ██║██║   ██║██████╔╝██║
    ██║██║   ██║██╔═══╝ ██║
    ██║╚██████╔╝██║     ██║
    ╚═╝ ╚═════╝ ╚═╝     ╚═╝
    Is Her :)
    Pharos Daily BOT
    """
    print(Fore.MAGENTA + banner)

def wait_until_730am():
    jakarta_timezone = pytz.timezone('Asia/Jakarta')
    current_time = datetime.now(jakarta_timezone)
    next_run_time = current_time.replace(hour=7, minute=30, second=0, microsecond=0)
    if current_time >= next_run_time:
        next_run_time += timedelta(days=1)
    wait_time = (next_run_time - current_time).total_seconds()
    hours, remainder = divmod(wait_time, 3600)
    minutes = remainder // 60
    print(f"{Fore.YELLOW}⏳ Waiting for next loop at 7:30 AM WIB: {int(hours)}h {int(minutes)}m{Style.RESET_ALL}")
    time.sleep(wait_time)

def generate_signature(private_key, message="pharos"):
    w3 = Web3()
    msg = encode_defunct(text=message)
    signed_msg = w3.eth.account.sign_message(msg, private_key=private_key)
    signature = signed_msg.signature.hex()
    return signature if signature.startswith("0x") else f"0x{signature}"

def get_jwt(address, signature, proxy):
    url = f"{BASE_URL}/user/login?address={address}&signature={signature}"
    headers = HEADERS_TEMPLATE.copy()
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=30)
            if response.status_code in (200, 201):
                data = response.json()
                if data.get("code") == 0:
                    print(f"{Fore.GREEN}🔐 JWT obtained successfully {Style.RESET_ALL}")
                    return data["data"]["jwt"]
                raise Exception(f"JWT error: {data}")
            print(f"{Fore.YELLOW}⚠️ Attempt {attempt}: Status {response.status_code} {Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Attempt {attempt}: JWT fetch failed : {e}{Style.RESET_ALL}")
        time.sleep(BACKOFF_FACTOR ** attempt)
    return None

def sign_in(address, jwt_token, proxy):
    url = f"{BASE_URL}/sign/in"
    params = {"address": address}
    headers = HEADERS_TEMPLATE.copy()
    headers['authorization'] = f"Bearer {jwt_token}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, params=params, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=30)
            if response.status_code in (200, 201):
                print(f"{Fore.GREEN}✅ Signed in successfully {Style.RESET_ALL}")
                return response.json()
            print(f"{Fore.YELLOW}⚠️ Attempt {attempt}: Sign-in failed, status {response.status_code} {Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Attempt {attempt}: Sign-in error : {e}{Style.RESET_ALL}")
        time.sleep(BACKOFF_FACTOR ** attempt)
    print(f"{Fore.RED}❌ Sign-in failed after {MAX_RETRIES} attempts {Style.RESET_ALL}")
    return None

def get_profile(address, jwt_token, proxy):
    url = f"{BASE_URL}/user/profile?address={address}"
    headers = HEADERS_TEMPLATE.copy()
    headers['authorization'] = f"Bearer {jwt_token}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=30)
            if response.status_code in (200, 201):
                data = response.json()
                if data.get("code") == 0:
                    print(f"{Fore.GREEN}📋 Profile fetched successfully {Style.RESET_ALL}")
                    return data["data"]["user_info"]
                raise Exception(f"Profile error: {data}")
            print(f"{Fore.YELLOW}⚠️ Attempt {attempt}: Profile fetch failed, status {response.status_code} {Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Attempt {attempt}: Profile fetch error : {e}{Style.RESET_ALL}")
        time.sleep(BACKOFF_FACTOR ** attempt)
    return None

def get_tasks(address, jwt_token, proxy):
    url = f"{BASE_URL}/user/tasks?address={address}"
    headers = HEADERS_TEMPLATE.copy()
    headers['authorization'] = f"Bearer {jwt_token}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=30)
            if response.status_code in (200, 201):
                data = response.json()
                if data.get("code") == 0:
                    print(f"{Fore.GREEN}📋 Tasks fetched successfully {Style.RESET_ALL}")
                    return data["data"]["user_tasks"]
                raise Exception(f"Task error: {data}")
            print(f"{Fore.YELLOW}⚠️ Attempt {attempt}: Task fetch failed, status {response.status_code} {Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Attempt {attempt}: Task fetch error : {e}{Style.RESET_ALL}")
        time.sleep(BACKOFF_FACTOR ** attempt)
    return None

def get_latest_nonce(w3, wallet_address):
    global nonce_cache
    try:
        pending_nonce = w3.eth.get_transaction_count(wallet_address, 'pending')
        latest_nonce = w3.eth.get_transaction_count(wallet_address, 'latest')
        current_nonce = max(pending_nonce, latest_nonce)
        nonce_cache[wallet_address] = current_nonce
        return current_nonce
    except Exception as e:
        print(f"{Fore.RED}❌ Nonce fetch error for {wallet_address[:10]}...: {e}{Style.RESET_ALL}")
        return nonce_cache.get(wallet_address, w3.eth.get_transaction_count(wallet_address, 'latest'))

def increment_nonce(wallet_address):
    global nonce_cache
    current_nonce = nonce_cache.get(wallet_address, 0)
    nonce_cache[wallet_address] = current_nonce + 1
    return current_nonce + 1

def send_native_tx(w3, account, to_address, amount_eth):
    wallet_address = account.address
    WAIT_TIMEOUT = 300
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            nonce = get_latest_nonce(w3, wallet_address)
            gas_price = int(w3.eth.gas_price * 1.5)
            tx = {
                'to': to_address,
                'value': w3.to_wei(amount_eth, 'ether'),
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': w3.eth.chain_id,
            }
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = w3.to_hex(tx_hash)
            print(f"    {Fore.GREEN}🚀 TX Sent: {tx_hash_hex}{Style.RESET_ALL}")
            
            for wait_attempt in range(1, MAX_RETRIES + 1):
                try:
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=WAIT_TIMEOUT)
                    if receipt['status'] == 1:
                        increment_nonce(wallet_address)
                        return tx_hash_hex
                    else:
                        print(f"    {Fore.RED}❌ TX Failed: Transaction reverted{Style.RESET_ALL}")
                        return None
                except ValueError as wait_error:
                    if 'not in the chain after' in str(wait_error):
                        print(f"    {Fore.YELLOW}⚠️ Wait Attempt {wait_attempt}/{MAX_RETRIES}: Transaction not confirmed yet: {wait_error}{Style.RESET_ALL}")
                        if wait_attempt < MAX_RETRIES:
                            time.sleep(BACKOFF_FACTOR ** wait_attempt)
                            continue
                        print(f"    {Fore.RED}❌ TX not confirmed after {MAX_RETRIES} wait attempts{Style.RESET_ALL}")
                        return None
                except Exception as wait_error:
                    print(f"    {Fore.RED}❌ Wait Attempt {wait_attempt}/{MAX_RETRIES}: Receipt error: {wait_error}{Style.RESET_ALL}")
                    return None
        except ValueError as e:
            if 'nonce too low' in str(e) or 'TX_REPLAY_ATTACK' in str(e):
                print(f"    {Fore.YELLOW}⚠️ Attempt {attempt}: Nonce conflict: {e}{Style.RESET_ALL}")
                nonce_cache.pop(wallet_address, None)
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue
            print(f"    {Fore.RED}❌ Attempt {attempt}: TX error: {e}{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"    {Fore.RED}❌ Attempt {attempt}: TX error: {e}{Style.RESET_ALL}")
            return None
    print(f"    {Fore.RED}❌ TX failed after {MAX_RETRIES} attempts{Style.RESET_ALL}")
    return None

def verify_tx(address, jwt, tx_hash, proxy):
    url = f"{BASE_URL}/task/verify?address={address}&task_id={TASK_ID}&tx_hash={tx_hash}"
    headers = HEADERS_TEMPLATE.copy()
    headers['authorization'] = f"Bearer {jwt}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=30)
            if response.status_code in (200, 201):
                data = response.json()
                verified = data.get("data", {}).get("verified", False)
                if verified:
                    print(f"    {Fore.GREEN}✅ TX Verified {Style.RESET_ALL}")
                    return verified
                print(f"    {Fore.YELLOW}⚠️ TX Not Verified {Style.RESET_ALL}")
                verify_retries = 0
                while not verified and verify_retries < 10:
                    verify_retries += 1
                    print(f"    {Fore.YELLOW}🔄 Retrying verification ({verify_retries}/10) ...{Style.RESET_ALL}")
                    time.sleep(10)
                    retry_response = requests.post(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=30)
                    if retry_response.status_code in (200, 201):
                        retry_data = retry_response.json()
                        verified = retry_data.get("data", {}).get("verified", False)
                        if verified:
                            print(f"    {Fore.GREEN}✅ TX Verified {Style.RESET_ALL}")
                            return verified
                        print(f"    {Fore.YELLOW}⚠️ Still not verified {Style.RESET_ALL}")
                    else:
                        print(f"    {Fore.YELLOW}⚠️ Retry {verify_retries}: Status {retry_response.status_code} {Style.RESET_ALL}")
                return verified
            print(f"    {Fore.YELLOW}⚠️ Attempt {attempt}: Status {response.status_code} {Style.RESET_ALL}")
        except Exception as e:
            print(f"    {Fore.RED}❌ Attempt {attempt}: Verification error : {e}{Style.RESET_ALL}")
        time.sleep(BACKOFF_FACTOR ** attempt)
    print(f"    {Fore.RED}❌ Verification failed after retries {Style.RESET_ALL}")
    return False

def get_to_addresses(wallet_index, proxy):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://testnet.pharosscan.xyz',
        'priority': 'u=1, i',
        'referer': 'https://testnet.pharosscan.xyz/',
        'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }
    base_url = 'https://api.socialscan.io/pharos-testnet/v1/explorer/transactions'
    address = '0xf8a1d4ff0f9b9af7ce58e1fc1833688f3bfd6115'
    target_count = 15
    unique_addresses = set()
    attempt_count = 0
    page = wallet_index if wallet_index <= 10 else 1
    w3 = Web3()
    while len(unique_addresses) < target_count:
        attempt_count += 1
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                params = {'size': '50', 'page': str(page), 'address': address}
                response = requests.get(base_url, params=params, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=30)
                if response.status_code in (200, 201):
                    data = response.json()
                    transactions = data.get("data", [])
                    if not transactions:
                        print(f"    {Fore.YELLOW}⚠️ Attempt {attempt_count}: No transactions on page {page} {Style.RESET_ALL}")
                        page = (page % 10) + 1
                        continue
                    new_addresses = 0
                    for tx in transactions:
                        from_address = tx.get("from_address")
                        if from_address:
                            checksum_address = w3.to_checksum_address(from_address)
                            if checksum_address not in unique_addresses:
                                unique_addresses.add(checksum_address)
                                new_addresses += 1
                    print(f"    {Fore.CYAN}🔍 Attempt {attempt_count}: Page {page}, {new_addresses} new addresses, Total: {len(unique_addresses)}/{target_count} {Style.RESET_ALL}")
                    page = (page % 10) + 1
                    break
                print(f"    {Fore.YELLOW}⚠️ Attempt {attempt_count}, Retry {attempt}: Status {response.status_code} {Style.RESET_ALL}")
            except Exception as e:
                print(f"    {Fore.RED}❌ Attempt {attempt_count}, Retry {attempt}: Fetch error : {e}{Style.RESET_ALL}")
            time.sleep(BACKOFF_FACTOR ** attempt)
        else:
            print(f"    {Fore.RED}❌ Failed to fetch addresses after {MAX_RETRIES} retries {Style.RESET_ALL}")
            return list(unique_addresses)[:target_count]
        time.sleep(10)
    print(f"    {Fore.GREEN}✅ Found {len(unique_addresses)} recipient addresses {Style.RESET_ALL}")
    return list(unique_addresses)[:target_count]

def get_token_balance(w3, token_contract, decimals, wallet_address):
    try:
        balance = token_contract.functions.balanceOf(wallet_address).call()
        return balance, round(balance / (10 ** decimals), 4)
    except Exception as e:
        print(f"{Fore.RED}❌ Balance fetch error for {token_contract.address}: {e}{Style.RESET_ALL}")
        raise

def print_eth_balance(w3, wallet_address):
    bal = w3.eth.get_balance(wallet_address)
    print(f"   {Fore.YELLOW}💰 PHRS: {round(w3.from_wei(bal, 'ether'), 4)} PHRS{Style.RESET_ALL}")
    return bal

def swap_native_to_token(w3, token_address, amount_in_eth, token_symbol, token_contract, token_decimals, wallet_address, private_key):
    amount_in_eth = round(amount_in_eth, 4)
    print(f"    {Fore.CYAN}🔄 Swapping {amount_in_eth:.4f} PHRS to {token_symbol}...{Style.RESET_ALL}")
    amount_in_wei = w3.to_wei(amount_in_eth, 'ether')
    deadline = int(time.time()) + DEADLINE_MINUTES * 60
    params = {
        "tokenIn": WPHRS_CONTRACT_ADDRESS,
        "tokenOut": token_address,
        "fee": FEE,
        "recipient": wallet_address,
        "amountIn": amount_in_wei,
        "amountOutMinimum": 0,
        "sqrtPriceLimitX96": 0
    }
    router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)
    try:
        estimated = router.functions.exactInputSingle(params).call({"from": wallet_address, "value": amount_in_wei})
        print(f"    {Fore.YELLOW}📊 Estimated: {amount_in_eth:.4f} PHRS → ~{round(estimated / (10 ** token_decimals), 4)} {token_symbol}{Style.RESET_ALL}")
    except Exception as e:
        print(f"    {Fore.RED}❌ Estimation failed: {e}{Style.RESET_ALL}")
        return None, 0
    multicall_data = [router.functions.exactInputSingle(params).build_transaction({"from": wallet_address, "value": amount_in_wei})['data']]
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            nonce = get_latest_nonce(w3, wallet_address)
            gas = router.functions.multicall(deadline, multicall_data).estimate_gas({"from": wallet_address, "value": amount_in_wei, "nonce": nonce})
            gas_price = int(w3.eth.gas_price * 1.2)
            txn = router.functions.multicall(deadline, multicall_data).build_transaction({
                "from": wallet_address,
                "value": amount_in_wei,
                "nonce": nonce,
                "gas": int(gas * 1.2),
                "gasPrice": gas_price,
                "chainId": w3.eth.chain_id
            })
            signed = w3.eth.account.sign_transaction(txn, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            tx_hash_hex = w3.to_hex(tx_hash)
            print(f"    {Fore.GREEN}🚀 TX Sent: {tx_hash_hex}{Style.RESET_ALL}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            if receipt['status'] == 1:
                print(f"    {Fore.GREEN}✅ Swap to {token_symbol} successful{Style.RESET_ALL}")
                _, balance = get_token_balance(w3, token_contract, token_decimals, wallet_address)
                print(f"    {Fore.YELLOW}💰 {token_symbol}: {balance:.4f}{Style.RESET_ALL}")
                increment_nonce(wallet_address)
                return tx_hash_hex, balance
            print(f"    {Fore.RED}❌ Swap to {token_symbol} failed: Transaction reverted{Style.RESET_ALL}")
            return None, 0
        except Exception as e:
            if 'TX_REPLAY_ATTACK' in str(e) or 'nonce too low' in str(e):
                print(f"{Fore.YELLOW}⚠️ Attempt {attempt}: Nonce conflict: {e}{Style.RESET_ALL}")
                nonce_cache.pop(wallet_address, None)
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue
            print(f"    {Fore.RED}❌ Attempt {attempt}: Swap to {token_symbol} failed: {e}{Style.RESET_ALL}")
            return None, 0
    print(f"    {Fore.RED}❌ Swap to {token_symbol} failed after {MAX_RETRIES} attempts{Style.RESET_ALL}")
    return None, 0

def swap_token_to_native(w3, token_address, token_contract, token_decimals, token_symbol, wallet_address, private_key):
    raw_bal, bal = get_token_balance(w3, token_contract, token_decimals, wallet_address)
    if raw_bal == 0:
        print(f"{Fore.YELLOW}⚠️ No {token_symbol} to swap{Style.RESET_ALL}")
        return None
    amount_in = int(raw_bal * 0.9)
    amount_in_readable = round(amount_in / (10**token_decimals), 4)
    print(f"    {Fore.CYAN}🔄 Swapping 90% of {token_symbol} ({amount_in_readable:.4f} {token_symbol}) to PHRS...{Style.RESET_ALL}")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            nonce = get_latest_nonce(w3, wallet_address)
            approve_tx = token_contract.functions.approve(ROUTER_ADDRESS, amount_in).build_transaction({
                "from": wallet_address,
                "nonce": nonce,
                "gas": 60000,
                "gasPrice": int(w3.eth.gas_price * 1.2),
                "chainId": w3.eth.chain_id
            })
            signed_approve = w3.eth.account.sign_transaction(approve_tx, private_key)
            approve_tx_hash = w3.eth.send_raw_transaction(signed_approve.raw_transaction)
            print(f"    {Fore.GREEN}🚀 {token_symbol} Approval TX Sent: {w3.to_hex(approve_tx_hash)}{Style.RESET_ALL}")
            w3.eth.wait_for_transaction_receipt(approve_tx_hash, timeout=300)
            print(f"    {Fore.GREEN}✅ {token_symbol} Approval confirmed{Style.RESET_ALL}")
            increment_nonce(wallet_address)
            break
        except Exception as e:
            if 'TX_REPLAY_ATTACK' in str(e) or 'nonce too low' in str(e):
                print(f"    {Fore.YELLOW}⚠️ Attempt {attempt}: Nonce conflict in approval: {e}{Style.RESET_ALL}")
                nonce_cache.pop(wallet_address, None)
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue
            print(f"    {Fore.RED}❌ Attempt {attempt}: {token_symbol} Approval failed: {e}{Style.RESET_ALL}")
            return None
    else:
        print(f"    {Fore.RED}❌ {token_symbol} Approval failed after {MAX_RETRIES} attempts{Style.RESET_ALL}")
        return None
    params = {
        "tokenIn": token_address,
        "tokenOut": WPHRS_CONTRACT_ADDRESS,
        "fee": FEE,
        "recipient": "0x0000000000000000000000000000000000000002",
        "amountIn": amount_in,
        "amountOutMinimum": 0,
        "sqrtPriceLimitX96": 0
    }
    router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)
    try:
        estimated = router.functions.exactInputSingle(params).call({"from": wallet_address})
        params["amountOutMinimum"] = int(estimated * 0.95)
        print(f"    {Fore.YELLOW}📊 Estimated: {amount_in_readable:.4f} {token_symbol} → ~{round(w3.from_wei(estimated, 'ether'), 4)} PHRS{Style.RESET_ALL}")
    except Exception as e:
        print(f"    {Fore.RED}❌ Estimation failed: {e}{Style.RESET_ALL}")
        return None
    swap_data = router.functions.exactInputSingle(params).build_transaction({"from": wallet_address})['data']
    unwrap_data = router.functions.unwrapWETH9(0, wallet_address).build_transaction({"from": wallet_address})['data']
    multicall_data = [swap_data, unwrap_data]
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            nonce = get_latest_nonce(w3, wallet_address)
            gas = router.functions.multicall(int(time.time()) + DEADLINE_MINUTES * 60, multicall_data).estimate_gas({"from": wallet_address, "nonce": nonce})
            txn = router.functions.multicall(int(time.time()) + DEADLINE_MINUTES * 60, multicall_data).build_transaction({
                "from": wallet_address,
                "nonce": nonce,
                "gas": int(gas * 1.2),
                "gasPrice": int(w3.eth.gas_price * 1.2),
                "chainId": w3.eth.chain_id
            })
            signed_tx = w3.eth.account.sign_transaction(txn, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = w3.to_hex(tx_hash)
            print(f"    {Fore.GREEN}🚀 TX Sent: {tx_hash_hex}{Style.RESET_ALL}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            if receipt['status'] == 1:
                print(f"    {Fore.GREEN}✅ Swap {token_symbol} to PHRS successful{Style.RESET_ALL}")
                print_eth_balance(w3, wallet_address)
                increment_nonce(wallet_address)
                return tx_hash_hex
            print(f"    {Fore.RED}❌ Swap {token_symbol} to PHRS failed: Transaction reverted{Style.RESET_ALL}")
            return None
        except Exception as e:
            if 'TX_REPLAY_ATTACK' in str(e) or 'nonce too low' in str(e):
                print(f"    {Fore.YELLOW}⚠️ Attempt {attempt}: Nonce conflict: {e}{Style.RESET_ALL}")
                nonce_cache.pop(wallet_address, None)
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue
            print(f"    {Fore.RED}❌ Attempt {attempt}: Swap {token_symbol} to PHRS failed: {e}{Style.RESET_ALL}")
            return None
    print(f"    {Fore.RED}❌ Swap {token_symbol} to PHRS failed after {MAX_RETRIES} attempts{Style.RESET_ALL}")
    return None

def add_liquidity_native_erc20(w3, amount_native_in_eth, target_token_contract, target_token_address, target_token_decimals, target_token_symbol, pool_fee, tick_lower, tick_upper, wallet_address, private_key):
    amount_native_in_eth = round(amount_native_in_eth, 4)
    print(f"    {Fore.CYAN}💧 Adding liquidity with {amount_native_in_eth:.4f} PHRS and {target_token_symbol}...{Style.RESET_ALL}")
    MINIMUM_PHRS = 0.00001
    if amount_native_in_eth < MINIMUM_PHRS:
        print(f"    {Fore.YELLOW}⚠️ Amount {amount_native_in_eth:.4f} PHRS below minimum ({MINIMUM_PHRS} PHRS) for {target_token_symbol} liquidity{Style.RESET_ALL}")
        return None
    amount_native_in_wei = w3.to_wei(amount_native_in_eth, 'ether')
    quoter = w3.eth.contract(address=QUOTER_ADDRESS, abi=QUOTER_ABI)
    quote_params = (
        WPHRS_CONTRACT_ADDRESS,
        target_token_address,
        amount_native_in_wei,
        pool_fee,
        0
    )
    try:
        quote_result = quoter.functions.quoteExactInputSingle(quote_params).call()
        estimated_target_token_amount_wei = quote_result[0]
        estimated_target_token_readable = round(estimated_target_token_amount_wei / (10**target_token_decimals), 4)
        print(f"    {Fore.YELLOW}📊 Estimated: {amount_native_in_eth:.4f} PHRS → ~{estimated_target_token_readable:.4f} {target_token_symbol}{Style.RESET_ALL}")
    except Exception as e:
        print(f"    {Fore.RED}❌ Quoting failed for {target_token_symbol}: {e}{Style.RESET_ALL}")
        return None
    token_balance_wei, token_balance_readable = get_token_balance(w3, target_token_contract, target_token_decimals, wallet_address)
    if token_balance_wei < estimated_target_token_amount_wei:
        print(f"    {Fore.YELLOW}⚠️ Insufficient {target_token_symbol} balance: {token_balance_readable:.4f}, needed: {estimated_target_token_readable:.4f}{Style.RESET_ALL}")
        return None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            nonce_approve = get_latest_nonce(w3, wallet_address)
            approve_tx = target_token_contract.functions.approve(NONFUNGIBLE_POSITION_MANAGER_ADDRESS, estimated_target_token_amount_wei).build_transaction({
                "from": wallet_address,
                "nonce": nonce_approve,
                "gas": 100000,
                "gasPrice": int(w3.eth.gas_price * 1.2),
                "chainId": w3.eth.chain_id
            })
            signed_approve_tx = w3.eth.account.sign_transaction(approve_tx, private_key)
            approve_tx_hash = w3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
            print(f"    {Fore.GREEN}🚀 Approval TX Sent: {w3.to_hex(approve_tx_hash)}{Style.RESET_ALL}")
            w3.eth.wait_for_transaction_receipt(approve_tx_hash, timeout=600)
            print(f"    {Fore.GREEN}✅ Approval confirmed{Style.RESET_ALL}")
            increment_nonce(wallet_address)
            break
        except Exception as e:
            if 'TX_REPLAY_ATTACK' in str(e) or 'nonce too low' in str(e):
                print(f"    {Fore.YELLOW}⚠️ Attempt {attempt}: Nonce conflict in approval: {e}{Style.RESET_ALL}")
                nonce_cache.pop(wallet_address, None)
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue
            print(f"    {Fore.RED}❌ Attempt {attempt}: Approval failed: {e}{Style.RESET_ALL}")
            return None
    else:
        print(f"    {Fore.RED}❌ Approval failed after {MAX_RETRIES} attempts{Style.RESET_ALL}")
        return None
    deadline = int(time.time()) + DEADLINE_MINUTES * 60
    if WPHRS_CONTRACT_ADDRESS.lower() < target_token_address.lower():
        token0_pool_addr = WPHRS_CONTRACT_ADDRESS
        token1_pool_addr = target_token_address
        amount0_desired_for_mint = amount_native_in_wei
        amount1_desired_for_mint = estimated_target_token_amount_wei
    else:
        token0_pool_addr = target_token_address
        token1_pool_addr = WPHRS_CONTRACT_ADDRESS
        amount0_desired_for_mint = estimated_target_token_amount_wei
        amount1_desired_for_mint = amount_native_in_wei
    print(f"    {Fore.CYAN}🏊‍♂️ Pool: Token0={token0_pool_addr[:8]}..., Token1={token1_pool_addr[:8]}...{Style.RESET_ALL}")
    nonfungible_pm = w3.eth.contract(address=NONFUNGIBLE_POSITION_MANAGER_ADDRESS, abi=NONFUNGIBLE_PM_ABI)
    mint_params = (
        token0_pool_addr,
        token1_pool_addr,
        pool_fee,
        tick_lower,
        tick_upper,
        amount0_desired_for_mint,
        amount1_desired_for_mint,
        0,
        0,
        wallet_address,
        deadline
    )
    mint_calldata = nonfungible_pm.functions.mint(mint_params).build_transaction({'from': wallet_address, 'gas': 0})['data']
    refund_eth_calldata = nonfungible_pm.functions.refundETH().build_transaction({'from': wallet_address, 'gas': 0})['data']
    multicall_payload = [mint_calldata, refund_eth_calldata]
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            nonce_multicall = get_latest_nonce(w3, wallet_address)
            estimated_gas = nonfungible_pm.functions.multicall(multicall_payload).estimate_gas({
                "from": wallet_address, "value": amount_native_in_wei, "nonce": nonce_multicall
            })
            multicall_tx = nonfungible_pm.functions.multicall(multicall_payload).build_transaction({
                "from": wallet_address, "value": amount_native_in_wei, "nonce": nonce_multicall,
                "gas": int(estimated_gas * 1.25),
                "gasPrice": int(w3.eth.gas_price * 1.2), "chainId": w3.eth.chain_id
            })
            signed_multicall_tx = w3.eth.account.sign_transaction(multicall_tx, private_key)
            multicall_tx_hash = w3.eth.send_raw_transaction(signed_multicall_tx.raw_transaction)
            tx_hash_hex = w3.to_hex(multicall_tx_hash)
            print(f"    {Fore.GREEN}🚀 Add Liquidity TX Sent: {tx_hash_hex}{Style.RESET_ALL}")
            receipt = w3.eth.wait_for_transaction_receipt(multicall_tx_hash, timeout=600)
            if receipt['status'] == 1:
                print(f"    {Fore.GREEN}✅ Add Liquidity for {target_token_symbol} successful{Style.RESET_ALL}")
                increment_nonce(wallet_address)
                return tx_hash_hex
            print(f"    {Fore.RED}❌ Add Liquidity for {target_token_symbol} failed: Transaction reverted{Style.RESET_ALL}")
            return None
        except Exception as e:
            if 'TX_REPLAY_ATTACK' in str(e) or 'nonce too low' in str(e):
                print(f"    {Fore.YELLOW}⚠️ Attempt {attempt}: Nonce conflict: {e}{Style.RESET_ALL}")
                nonce_cache.pop(wallet_address, None)
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue
            print(f"    {Fore.RED}❌ Attempt {attempt}: Add Liquidity for {target_token_symbol} failed: {e}{Style.RESET_ALL}")
            return None
    print(f"    {Fore.RED}❌ Add Liquidity for {target_token_symbol} failed after {MAX_RETRIES} attempts{Style.RESET_ALL}")
    return None

def process_wallet(wallet_index, pk, total_wallets, proxy):
    try:
        w3 = Web3(HTTPProvider(RPC_URL, request_kwargs={'proxies': {'http': proxy, 'https': proxy}}))
        try:
            w3.eth.get_block('latest')
            print(f"{Fore.GREEN}✅ Network connection established {Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Network error : {e}{Style.RESET_ALL}")
            return

        account = Account.from_key(pk)
        wallet_address = account.address
        print(f"{Fore.WHITE}═╣ Wallet {wallet_index}/{total_wallets}: {wallet_address[:10]}... ╠═{Style.RESET_ALL}")

        usdc_contract = w3.eth.contract(address=USDC_TOKEN, abi=ERC20_ABI)
        usdt_contract = w3.eth.contract(address=USDT_TOKEN, abi=ERC20_ABI)
        usdc_decimals = usdc_contract.functions.decimals().call()
        usdt_decimals = usdt_contract.functions.decimals().call()
        
        print(f"{Fore.WHITE}═╣ AUTHENTICATION ╠═{Style.RESET_ALL}")
        signature = generate_signature(pk)
        print(f"{Fore.CYAN}🔏 Signature: {signature[:10]}...{signature[-10:]}{Style.RESET_ALL}")
        jwt = get_jwt(wallet_address, signature, proxy)
        if not jwt:
            print(f"{Fore.RED}❌ Failed to get JWT {Style.RESET_ALL}")
            return
        print(f"🛡️ JWT: {Fore.GREEN}Authenticated!{Style.RESET_ALL}")

        sign_in_result = sign_in(wallet_address, jwt, proxy)
        print(f"{Fore.CYAN}📝 Sign-in: {sign_in_result}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}═╣ PROFILE & TASKS ╠═{Style.RESET_ALL}")
        profile = get_profile(wallet_address, jwt, proxy)
        if profile:
            print(f"    {Fore.YELLOW}🏆 Total Points: {profile.get('TotalPoints', 0)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to fetch profile {Style.RESET_ALL}")
            return

        tasks = get_tasks(wallet_address, jwt, proxy)
        task_descriptions = {
            101: "Total Swap",
            102: "Total Add Liquidity",
            103: "Total Send to Friend",
            201: "Social Media Task",
            202: "Social Media Task",
            203: "Social Media Task",
            204: "Social Media Task",
        }
        if tasks:
            for task in tasks:
                task_id = task['TaskId']
                complete_times = task['CompleteTimes']
                description = task_descriptions.get(task_id, "Unknown Task")
                print(f"    {Fore.YELLOW}📋 Task {task_id} ({description}): {complete_times}x completed{Style.RESET_ALL}")
        else:
            print(f"    {Fore.RED}❌ Failed to fetch tasks {Style.RESET_ALL}")

        print(f"{Fore.WHITE}═╣ SEND TO FRIEND OPERATION ╠═{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔍 Fetching target addresses...{Style.RESET_ALL}")
        to_addresses = get_to_addresses(wallet_index, proxy)
        if not to_addresses:
            print(f"{Fore.RED}❌ Failed to get target addresses {Style.RESET_ALL}")
            return
        print(f"{Fore.GREEN}✅ Found {len(to_addresses)} recipient addresses {Style.RESET_ALL}")

        for idx, to_address in enumerate(to_addresses, start=1):
            amount_eth = round(random.uniform(0.00001, 0.00005), 6)
            print(f"{Fore.CYAN}💸 Sending {amount_eth:.6f} PHRS to {to_address[:10]}... ({idx}/{len(to_addresses)}){Style.RESET_ALL}")
            try:
                tx_hash = send_native_tx(w3, account, to_address, amount_eth)
                if tx_hash:
                    w3.eth.wait_for_transaction_receipt(tx_hash)
                    time.sleep(5)
                    verify_tx(wallet_address, jwt, tx_hash, proxy)
                    time.sleep(3)
            except Exception as e:
                print(f"{Fore.RED}❌ Transaction error: {e}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}═╣ Swap & Liquidity Operations 🏊‍♂️ ╠═{Style.RESET_ALL}")
        pool_fee_swap = 500
        pool_fee_liquidity = 10000
        tick_lower = 72800
        tick_upper = 86800

        for i in range(50):
            print(f"{Fore.WHITE}═══ Iteration {i+1}/50 🔄 ═══{Style.RESET_ALL}")
            try:
                print(f"{Fore.CYAN}💰 Initial Balances{Style.RESET_ALL}")
                initial_eth_balance_wei = print_eth_balance(w3, wallet_address)
                _, usdc_balance = get_token_balance(w3, usdc_contract, usdc_decimals, wallet_address)
                _, usdt_balance = get_token_balance(w3, usdt_contract, usdt_decimals, wallet_address)
                print(f"{Fore.YELLOW}   💰 USDC: {usdc_balance:.4f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   💰 USDT: {usdt_balance:.4f}{Style.RESET_ALL}")

                if initial_eth_balance_wei < w3.to_wei(0.001, 'ether'):
                    print(f"{Fore.YELLOW}⚠️ Insufficient PHRS balance, skipping iteration{Style.RESET_ALL}")
                    continue

                print(f"{Fore.CYAN}🔄 Performing Swaps{Style.RESET_ALL}")
                swap_amount_eth = round(random.uniform(0.001, 0.005), 4)
                tx_hash_usdc, usdc_balance = swap_native_to_token(
                    w3, USDC_TOKEN, swap_amount_eth, "USDC", usdc_contract, usdc_decimals,
                    wallet_address, pk
                )
                time.sleep(10)
                swap_amount_eth = round(random.uniform(0.001, 0.005), 4)
                tx_hash_usdt, usdt_balance = swap_native_to_token(
                    w3, USDT_TOKEN, swap_amount_eth, "USDT", usdt_contract, usdt_decimals,
                    wallet_address, pk
                )

                print(f"{Fore.CYAN}💰 Balances After Swaps{Style.RESET_ALL}")
                current_eth_balance_wei = print_eth_balance(w3, wallet_address)
                _, usdc_balance = get_token_balance(w3, usdc_contract, usdc_decimals, wallet_address)
                _, usdt_balance = get_token_balance(w3, usdt_contract, usdt_decimals, wallet_address)
                print(f"{Fore.YELLOW}   💰 USDC: {usdc_balance:.4f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   💰 USDT: {usdt_balance:.4f}{Style.RESET_ALL}")

                print(f"{Fore.CYAN}💧 Adding Liquidity{Style.RESET_ALL}")
                amount_to_add_eth = round(random.uniform(0.0001, 0.0005), 4)
                if initial_eth_balance_wei < w3.to_wei(amount_to_add_eth, 'ether'):
                    print(f"{Fore.YELLOW}⚠️ Insufficient PHRS for liquidity, skipping USDC liquidity{Style.RESET_ALL}")
                elif tx_hash_usdc:
                    add_liquidity_native_erc20(
                        w3, amount_to_add_eth, usdc_contract, USDC_TOKEN, usdc_decimals, "USDC",
                        pool_fee_liquidity, tick_lower, tick_upper, wallet_address, pk
                    )
                else:
                    print(f"{Fore.YELLOW}⚠️ Skipping USDC liquidity due to failed swap{Style.RESET_ALL}")
                time.sleep(10)
                amount_to_add_eth = round(random.uniform(0.0001, 0.0005), 4)
                if initial_eth_balance_wei < w3.to_wei(amount_to_add_eth, 'ether'):
                    print(f"{Fore.YELLOW}⚠️ Insufficient PHRS for liquidity, skipping USDT liquidity{Style.RESET_ALL}")
                elif tx_hash_usdt:
                    add_liquidity_native_erc20(
                        w3, amount_to_add_eth, usdt_contract, USDT_TOKEN, usdt_decimals, "USDT",
                        pool_fee_liquidity, tick_lower, tick_upper, wallet_address, pk
                    )
                else:
                    print(f"{Fore.YELLOW}⚠️ Skipping USDT liquidity due to failed swap{Style.RESET_ALL}")

                print(f"{Fore.CYAN}💰 Balances After Liquidity{Style.RESET_ALL}")
                current_eth_balance_wei = print_eth_balance(w3, wallet_address)
                _, usdc_balance = get_token_balance(w3, usdc_contract, usdc_decimals, wallet_address)
                _, usdt_balance = get_token_balance(w3, usdt_contract, usdt_decimals, wallet_address)
                print(f"{Fore.YELLOW}   💰 USDC: {usdc_balance:.4f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   💰 USDT: {usdt_balance:.4f}{Style.RESET_ALL}")

                print(f"{Fore.CYAN}🔄 Swapping Back to PHRS{Style.RESET_ALL}")
                swap_back_usdc = swap_token_to_native(
                    w3, USDC_TOKEN, usdc_contract, usdc_decimals, "USDC", wallet_address, pk
                )
                time.sleep(10)
                swap_back_usdt = swap_token_to_native(
                    w3, USDT_TOKEN, usdt_contract, usdt_decimals, "USDT", wallet_address, pk
                )

                print(f"{Fore.CYAN}💰 Final Balances{Style.RESET_ALL}")
                print_eth_balance(w3, wallet_address)
                _, usdc_balance = get_token_balance(w3, usdc_contract, usdc_decimals, wallet_address)
                _, usdt_balance = get_token_balance(w3, usdt_contract, usdt_decimals, wallet_address)
                print(f"{Fore.YELLOW}   💰 USDC: {usdc_balance:.4f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   💰 USDT: {usdt_balance:.4f}{Style.RESET_ALL}")

                wait_time = random.uniform(3, 7)
                print(f"{Fore.YELLOW}⏳ Waiting {wait_time:.2f}s before next iteration...{Style.RESET_ALL}")
                time.sleep(wait_time)
            except Exception as e:
                print(f"{Fore.RED}❌ Iteration {i+1} failed: {e}{Style.RESET_ALL}")
                time.sleep(5)
                continue
    except Exception as e:
        print(f"{Fore.RED}❌ Wallet error : {e}{Style.RESET_ALL}")

def main():
    with open("pk.txt") as f:
        private_keys = [line.strip() for line in f if line.strip()]
    proxies = load_proxies()
    total_wallets = len(private_keys)

    if not proxies:
        print(f"{Fore.RED}❌ No proxies loaded. Exiting...{Style.RESET_ALL}")
        return

    if len(proxies) < total_wallets:
        print(f"{Fore.RED}❌ Not enough proxies ({len(proxies)}) for {total_wallets} private keys. Exiting...{Style.RESET_ALL}")
        return

    proxies = proxies[:total_wallets]
    used_proxies = set()
    proxy_assignments = []

    for i in range(total_wallets):
        proxy = get_working_proxy(proxies, used_proxies)
        if not proxy:
            print(f"{Fore.RED}❌ No working proxy found for wallet {i+1}. Exiting...{Style.RESET_ALL}")
            return
        used_proxies.add(proxy)
        proxy_assignments.append((i+1, private_keys[i], proxy))

    print(f"{Fore.WHITE}🏦 Total Wallets: {total_wallets}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Assigned {len(proxy_assignments)} proxies to wallets{Style.RESET_ALL}")

    for wallet_index, pk, proxy in proxy_assignments:
        try:
            process_wallet(wallet_index, pk, total_wallets, proxy)
        except Exception as e:
            print(f"{Fore.RED}❌ Wallet {wallet_index} execution failed: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        while True:
            clear_terminal()
            display_banner()
            main()
            wait_until_730am()
    except KeyboardInterrupt:
        print("\n🚪 Program dihentikan oleh pengguna. Keluar...")

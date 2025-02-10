import asyncio
import json
import base64
import struct
import base58
import hashlib
import websockets
import os
import argparse
from datetime import datetime
import logging

from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.system_program import TransferParams, transfer
from solders.transaction import VersionedTransaction

from spl.token.instructions import get_associated_token_address
import spl.token.instructions as spl_token

from config import *

# Import functions from buy.py
from buy import get_pump_curve_state, calculate_pump_curve_price, buy_token, listen_for_create_transaction

# Import functions from sell.py
from sell import sell_token

# Configure logging
logging.basicConfig(
    filename='trader.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_trade(action, token_data, price, tx_hash):
    os.makedirs("trades", exist_ok=True)
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "token_address": token_data['mint'],
        "price": price,
        "tx_hash": tx_hash
    }
    with open("trades/trades.log", 'a') as log_file:
        json.dump(log_entry, log_file)
        log_file.write("\n")

async def trade(websocket=None, match_string=None, bro_address=None, marry_mode=False, yolo_mode=False):
    if websocket is None:
        async with websockets.connect(WSS_ENDPOINT) as websocket:
            await _trade(websocket, match_string, bro_address, marry_mode, yolo_mode)
    else:
        await _trade(websocket, match_string, bro_address, marry_mode, yolo_mode)

async def _trade(websocket, match_string=None, bro_address=None, marry_mode=False, yolo_mode=False):
    while True:
        try:
            logging.info("Waiting for a new token creation...")
            token_data = await listen_for_create_transaction(websocket)
            logging.info(f"New token created: {token_data['name']}")

            # Apply token filters
            if not filter_tokens(token_data):
                logging.info("Token does not meet filter criteria. Skipping...")
                continue

            # Determine strategy based on pool size
            pool_size = token_data.get("pool_size", 0)
            strategy, params = get_strategy_parameters(pool_size)
            logging.info(f"Selected Strategy: {strategy}")

            # Use strategy parameters for trading
            buy_amount = params["buying_amount_wsol"]
            buy_slippage = params["buy_slippage"]
            sell_slippage = params["sell_slippage"]
            take_profit = params["take_profit"]
            stop_loss = params["stop_loss"]
            enforced_selling_time = params["enforced_selling_time_ms"] / 1000.0

            # Proceed with trading logic using the strategy parameters
            logging.info(f"Buying {buy_amount:.6f} WSOL worth of the new token with {buy_slippage*100:.1f}% slippage tolerance...")
            buy_tx_hash = await buy_token(mint, bonding_curve, associated_bonding_curve, amount=buy_amount, slippage=buy_slippage)
            if buy_tx_hash:
                logging.info(f"Buy transaction successful: {buy_tx_hash}")
            else:
                logging.warning("Buy transaction failed.")

            if not marry_mode:
                logging.info(f"Waiting for {enforced_selling_time} seconds before selling...")
                await asyncio.sleep(enforced_selling_time)

                logging.info(f"Selling tokens with {sell_slippage*100:.1f}% slippage tolerance...")
                sell_tx_hash = await sell_token(mint, bonding_curve, associated_bonding_curve, slippage=sell_slippage)
                if sell_tx_hash:
                    logging.info(f"Sell transaction successful: {sell_tx_hash}")
                else:
                    logging.warning("Sell transaction failed or no tokens to sell.")
            else:
                logging.info("Marry mode enabled. Skipping sell operation.")

            if not yolo_mode:
                break

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

async def main(yolo_mode=False, match_string=None, bro_address=None, marry_mode=False):
    if yolo_mode:
        while True:
            try:
                async with websockets.connect(WSS_ENDPOINT) as websocket:
                    while True:
                        try:
                            await trade(websocket, match_string, bro_address, marry_mode, yolo_mode)
                        except websockets.exceptions.ConnectionClosed:
                            print("WebSocket connection closed. Reconnecting...")
                            break
                        except Exception as e:
                            print(f"An error occurred: {e}")
                        print("Waiting for 5 seconds before looking for the next token...")
                        await asyncio.sleep(5)
            except Exception as e:
                print(f"Connection error: {e}")
                print("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
    else:
        # For non-YOLO mode, create a websocket connection and close it after one trade
        async with websockets.connect(WSS_ENDPOINT) as websocket:
            await trade(websocket, match_string, bro_address, marry_mode, yolo_mode)

async def ping_websocket(websocket):
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(20) # Send a ping every 20 seconds
        except:
            break

def filter_tokens(token_data):
    if FILTERS["check_freezable"] and token_data.get("is_freezable"):
        return False
    if FILTERS["check_lp_burned"] and token_data.get("lp_burned"):
        return False
    if FILTERS["skip_lp_bundles"] and token_data.get("is_lp_bundle"):
        return False
    if token_data.get("pool_size", 0) < FILTERS["min_pool_size"]:
        return False
    if token_data.get("dev_hold", 0) > FILTERS["max_dev_hold"]:
        return False
    return True

def get_strategy_parameters(pool_size):
    if pool_size < 100:
        strategy = "small_pool"
        params = {
            "buying_amount_wsol": 0.2,
            "take_profit": 0.10,
            "stop_loss": 0.08,
            "enforced_selling_time_ms": 60000,
            "buy_slippage": 0.40,
            "sell_slippage": 0.40,
            "price_check_interval_ms": 500
        }
    else:
        strategy = "large_pool"
        params = {
            "buying_amount_wsol": 0.5,
            "take_profit": 0.17,
            "stop_loss": 0.10,
            "enforced_selling_time_ms": 150000,
            "buy_slippage": 0.40,
            "sell_slippage": 0.40,
            "price_check_interval_ms": 500
        }
    return strategy, params

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trade tokens on Solana.")
    parser.add_argument("--yolo", action="store_true", help="Run in YOLO mode (continuous trading)")
    parser.add_argument("--match", type=str, help="Only trade tokens with names or symbols matching this string")
    parser.add_argument("--bro", type=str, help="Only trade tokens created by this user address")
    parser.add_argument("--marry", action="store_true", help="Only buy tokens, skip selling")
    args = parser.parse_args()
    asyncio.run(main(yolo_mode=args.yolo, match_string=args.match, bro_address=args.bro, marry_mode=args.marry))
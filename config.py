from solders.pubkey import Pubkey

# System & pump.fun addresses
PUMP_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
PUMP_FEE = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
PUMP_LIQUIDITY_MIGRATOR = Pubkey.from_string("39azUYFWPz3VHgKCf3VChUwbpURdCHRxjWVowf5jUJjg")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
SYSTEM_TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
SOL = Pubkey.from_string("So11111111111111111111111111111111111111112")
LAMPORTS_PER_SOL = 1_000_000_000

# Trading parameters
BUY_AMOUNT = 0.3  # WSOL
BUY_SLIPPAGE = 0.4  # 40% slippage tolerance for buying
SELL_SLIPPAGE = 0.4  # 40% slippage tolerance for selling
MAX_RETRIES = 3  # Number of retries for failed transactions

# Jito settings
JITO_TIPS_ENABLED = True
JITO_TIP_AMOUNT = 0.006  # SOL per transaction

# Wallet balance requirements
WALLET_BALANCE_REQUIREMENTS = {
    "sol": 1.0,  # For fees
    "wsol": 0.5  # Adjust based on strategy
}

# Selling parameters
AUTO_SELL = True
PRICE_CHECK_INTERVAL = 0.5  # seconds
TAKE_PROFIT = 0.13  # 13%
STOP_LOSS = 0.09  # 9%
ENFORCED_SELLING_TIME = 120  # seconds

# Token filters
FILTERS = {
    "check_freezable": True,
    "check_lp_burned": False,
    "skip_lp_bundles": True,
    "min_pool_size": 90,  # SOL
    "max_dev_hold": 0.1,  # 10%
    "socials_required": False
}

# Advanced settings
LOG_ANALYSIS_INTERVAL = 5  # seconds
WALLET_SETTINGS = {
    "dedicated_wallet": True,
    "auto_sweep_profits": True
}

# Your nodes
# You can also get a trader node https://docs.chainstack.com/docs/solana-trader-nodes
RPC_ENDPOINT = "https://young-dark-crater.solana-mainnet.quiknode.pro/58ea202484eebe007cc86f844f8ee50749d63d1e"
WSS_ENDPOINT = "wss://young-dark-crater.solana-mainnet.quiknode.pro/58ea202484eebe007cc86f844f8ee50749d63d1e"

#Private key
PRIVATE_KEY = "QN_dc1a75fd02124709b47bde57f128f9a7"

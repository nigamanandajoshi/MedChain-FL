"""
Secure key management for MedChain-FL.

Loads private keys and configuration exclusively from environment variables
(via .env for local dev, or a real secrets manager in production).
Private keys are NEVER stored in source code.
"""

import os
import re
from typing import Dict, Optional

from dotenv import load_dotenv
from web3 import Web3

from config.logging_config import get_logger

logger = get_logger(__name__)

# Load .env file if present (no-op in production where env vars come from the OS/secrets manager)
load_dotenv()

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

_PRIVATE_KEY_RE = re.compile(r'^0x[0-9a-fA-F]{64}$')


def _require_env(var: str) -> str:
    """Return the value of an environment variable, raising if it is missing."""
    value = os.environ.get(var)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{var}' is not set. "
            f"Copy .env.example to .env and fill in your values."
        )
    return value


def _validate_private_key(key: str, name: str) -> str:
    """Validate that a string looks like a 32-byte hex private key."""
    if not _PRIVATE_KEY_RE.match(key):
        raise ValueError(
            f"Environment variable '{name}' does not look like a valid private key "
            f"(expected 0x + 64 hex chars). Never hardcode keys — fix your .env file."
        )
    return key


def _validate_address(addr: str, name: str) -> str:
    """Validate and return a checksummed EIP-55 Ethereum address."""
    if not Web3.is_address(addr):
        raise ValueError(
            f"Environment variable '{name}' is not a valid Ethereum address: '{addr}'"
        )
    return Web3.to_checksum_address(addr)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_rpc_url() -> str:
    """Return the Ethereum RPC URL from the environment."""
    return os.environ.get("ETH_RPC_URL", "http://127.0.0.1:8545")


def get_admin_private_key() -> str:
    """Return the admin private key, validated."""
    raw = _require_env("ADMIN_PRIVATE_KEY")
    return _validate_private_key(raw, "ADMIN_PRIVATE_KEY")


def get_hospital_private_keys() -> Dict[str, str]:
    """
    Return a mapping of {hospital_name: private_key} loaded from the environment.
    Add new hospitals by extending the HOSPITAL_MAP below.
    """
    HOSPITAL_MAP = {
        "italy": "HOSPITAL_ITALY_PRIVATE_KEY",
        "pakistan": "HOSPITAL_PAKISTAN_PRIVATE_KEY",
        "usa": "HOSPITAL_USA_PRIVATE_KEY",
    }

    keys: Dict[str, str] = {}
    for hospital, env_var in HOSPITAL_MAP.items():
        raw = _require_env(env_var)
        keys[hospital] = _validate_private_key(raw, env_var)
    return keys


def get_contract_addresses() -> Optional[Dict[str, str]]:
    """
    Return contract addresses from environment variables if set,
    otherwise fall back to reading contract_addresses.json (written by deploy script).
    Always validates and checksums the address values.
    """
    gov_addr = os.environ.get("GOVERNANCE_CONTRACT_ADDRESS")
    ledger_addr = os.environ.get("LEDGER_CONTRACT_ADDRESS")

    if gov_addr and ledger_addr:
        return {
            "governance": _validate_address(gov_addr, "GOVERNANCE_CONTRACT_ADDRESS"),
            "ledger": _validate_address(ledger_addr, "LEDGER_CONTRACT_ADDRESS"),
        }

    # Fall back to JSON file (written by Hardhat deploy script on local devnet)
    import json
    json_path = "contract_addresses.json"
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        return {
            "governance": _validate_address(data["governance"], "governance"),
            "ledger": _validate_address(data["ledger"], "ledger"),
        }
    except FileNotFoundError:
        logger.error(
            f"'{json_path}' not found and GOVERNANCE_CONTRACT_ADDRESS / "
            f"LEDGER_CONTRACT_ADDRESS env vars are not set. "
            f"Run ./start_blockchain.sh first."
        )
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid contract address in '{json_path}': {e}")
        return None

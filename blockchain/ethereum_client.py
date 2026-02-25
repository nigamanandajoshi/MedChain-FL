"""Ethereum Blockchain Client Wrapper."""

import json
from typing import Dict, Any, Optional
from web3 import Web3
from eth_account import Account

from config.logging_config import get_logger

logger = get_logger(__name__)

# Gas safety multiplier applied on top of estimate_gas result
GAS_BUFFER_MULTIPLIER = 1.3


class EthereumClient:
    """Wrapper for web3.py interactions with the Ethereum blockchain."""

    def __init__(self, rpc_url: str = "http://127.0.0.1:8545"):
        """Initialize connection to Ethereum node."""
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Ethereum node at {rpc_url}")

        logger.info(f"Connected to Ethereum node at {rpc_url}")

    def load_contract(self, contract_address: str, abi_path: str) -> Any:
        """
        Load a smart contract instance.

        Args:
            contract_address: The deployed contract address (EIP-55 checksummed)
            abi_path: Path to the compiled contract's ABI JSON file

        Returns:
            web3 contract object
        """
        # Validate and checksum the address to catch typos early
        if not self.w3.is_address(contract_address):
            raise ValueError(f"Invalid contract address: '{contract_address}'")
        checksummed = self.w3.to_checksum_address(contract_address)

        with open(abi_path, 'r') as f:
            contract_data = json.load(f)

        # Hardhat compilation artifact: extract just the ABI array
        abi = contract_data.get('abi', contract_data)

        return self.w3.eth.contract(address=checksummed, abi=abi)

    def send_transaction(
        self,
        contract: Any,
        function_name: str,
        private_key: str,
        *args
    ) -> Dict[str, Any]:
        """
        Sign and send a transaction to a smart contract.

        Gas is estimated dynamically (with a safety buffer) instead of using
        a hardcoded value, so we never over- or under-pay.

        Args:
            contract: web3 contract instance
            function_name: Name of the function to call
            private_key: Private key of the sender
            *args: Arguments to pass to the contract function

        Returns:
            Transaction receipt dict

        Raises:
            ValueError: If the private key is malformed
            Exception: If the transaction reverts on-chain
        """
        account = Account.from_key(private_key)
        contract_function = getattr(contract.functions, function_name)

        nonce = self.w3.eth.get_transaction_count(account.address)

        # --- Dynamic gas estimation with safety buffer ---
        try:
            estimated_gas = contract_function(*args).estimate_gas(
                {'from': account.address}
            )
            gas_limit = int(estimated_gas * GAS_BUFFER_MULTIPLIER)
        except Exception as estimation_error:
            # Surface the revert reason from estimate_gas before we waste a TX
            raise RuntimeError(
                f"Gas estimation failed for '{function_name}' — "
                f"the transaction would revert. Reason: {estimation_error}"
            ) from estimation_error

        tx = contract_function(*args).build_transaction({
            'chainId': self.w3.eth.chain_id,
            'gas': gas_limit,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
            'from': account.address,
        })

        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)

        # Support both web3.py v6 (raw_transaction) and v5 (rawTransaction)
        raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
        if raw_tx is None:
            raise RuntimeError("Could not extract raw transaction from signed object.")

        logger.debug(f"Sending tx '{function_name}' from {account.address} (gas={gas_limit})")
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)  # type: ignore

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt['status'] != 1:
            raise RuntimeError(
                f"Transaction '{function_name}' reverted on-chain. "
                f"TX hash: {tx_receipt['transactionHash'].hex()}"
            )

        return tx_receipt

    def call_view_function(
        self,
        contract: Any,
        function_name: str,
        *args
    ) -> Any:
        """Call a view/pure contract function (no gas cost, no state change)."""
        contract_function = getattr(contract.functions, function_name)
        return contract_function(*args).call()

"""Blockchain ledger wrapper for model update tracking via Ethereum."""

import json
from typing import List, Dict, Optional
from config.logging_config import get_logger
from blockchain.ethereum_client import EthereumClient

logger = get_logger(__name__)


class BlockchainLedger:
    """Blockchain ledger wrapper for federated learning on Ethereum."""
    
    def __init__(self, eth_client: EthereumClient, contract_address: str, abi_path: str, admin_private_key: str):
        """
        Initialize connection to deployed ledger smart contract.
        
        Args:
            eth_client: EthereumClient instance
            contract_address: Deployed address of MedChainLedger
            abi_path: Path to the ABI JSON
            admin_private_key: Private key of the admin who deployed the contract
        """
        self.eth = eth_client
        self.contract = self.eth.load_contract(contract_address, abi_path)
        self.admin_pk = admin_private_key
        logger.info(f"Initialized smart contract ledger at {contract_address}")
    
    def record_fl_round(
        self,
        round_number: int,
        num_clients: int,
        global_metrics: Dict,
        model_hash: Optional[str] = None
    ) -> bool:
        """
        Record a federated learning round on the blockchain.
        
        Args:
            round_number: FL round number
            num_clients: Number of participating clients
            global_metrics: Aggregated metrics
            model_hash: Hash of global model weights
            
        Returns:
            True if recorded successfully
        """
        metrics_json = json.dumps(global_metrics)
        model_hash_str = model_hash if model_hash else ""
        
        try:
            receipt = self.eth.send_transaction(
                self.contract,
                'recordFLRound',
                self.admin_pk,
                round_number,
                num_clients,
                metrics_json,
                model_hash_str
            )
            logger.info(f"Recorded FL round {round_number} on-chain in tx {receipt['transactionHash'].hex()}")
            return True
        except Exception as e:
            logger.error(f"Failed to record FL round {round_number}: {str(e)}")
            return False
    
    def record_client_update(
        self,
        round_number: int,
        client_private_key: str,
        data_size: int,
        metrics: Dict
    ) -> bool:
        """
        Record a client update. Client signs this transaction themselves.
        
        Args:
            round_number: FL round number
            client_private_key: The Ethereum private key of the client sending the update
            data_size: Client dataset size
            metrics: Client metrics
            
        Returns:
            True if successful
        """
        metrics_json = json.dumps(metrics)
        
        try:
            receipt = self.eth.send_transaction(
                self.contract,
                'recordClientUpdate',
                client_private_key,
                round_number,
                data_size,
                metrics_json
            )
            logger.info(f"Client recorded update for round {round_number} in tx {receipt['transactionHash'].hex()}")
            return True
        except Exception as e:
            logger.error(f"Client failed to record update: {str(e)}")
            return False
            
    def get_fl_rounds(self) -> List[Dict]:
        """Get all FL round records from blockchain.
        This iterates from 1 to latestRound property on the contract.
        """
        rounds = []
        try:
            latest_round = self.eth.call_view_function(self.contract, 'latestRound')
            for i in range(1, latest_round + 1):
                round_data = self.eth.call_view_function(self.contract, 'flRounds', i)
                # Ensure the round exists (struct uninitialized value check)
                if round_data[0] != 0: 
                    rounds.append({
                        "round": round_data[0],
                        "num_clients": round_data[1],
                        "metrics": json.loads(round_data[2]) if round_data[2] else {},
                        "model_hash": round_data[3],
                        "timestamp": round_data[4]
                    })
        except Exception as e:
            logger.error(f"Failed to fetch FL rounds: {str(e)}")
            
        return rounds

    def get_client_updates(self, round_number: int) -> List[Dict]:
        """Get client updates for a specific round."""
        updates = []
        try:
            updates_data = self.eth.call_view_function(self.contract, 'getClientUpdates', round_number)
            for update in updates_data:
                updates.append({
                    "client_address": update[0],
                    "round": update[1],
                    "data_size": update[2],
                    "metrics": json.loads(update[3]) if update[3] else {},
                    "timestamp": update[4]
                })
        except Exception as e:
            logger.error(f"Failed to fetch client updates for round {round_number}: {str(e)}")
            
        return updates

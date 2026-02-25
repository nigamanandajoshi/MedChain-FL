"""Smart contract for federated learning governance."""

from typing import Dict, List, Optional
from datetime import datetime
from config.logging_config import get_logger
from blockchain.ethereum_client import EthereumClient

logger = get_logger(__name__)


class SmartContract:
    """Smart contract wrapper for FL governance and access control via Ethereum."""
    
    def __init__(self, eth_client: EthereumClient, contract_address: str, abi_path: str, admin_private_key: str):
        """
        Initialize connection to deployed governance smart contract.
        
        Args:
            eth_client: EthereumClient instance
            contract_address: Deployed address of MedChainGovernance
            abi_path: Path to the ABI JSON
            admin_private_key: Private key of the admin who deployed the contract
        """
        self.eth = eth_client
        self.contract = self.eth.load_contract(contract_address, abi_path)
        self.admin_pk = admin_private_key
        
        # Access logs (kept off-chain for cheaper logging, could be moved on-chain if needed)
        self.access_log: List[Dict] = []
        
        # Read initial params from blockchain
        self.min_clients = self.eth.call_view_function(self.contract, 'minClients')
        self.min_data_quality = self.eth.call_view_function(self.contract, 'minDataQuality') / 100.0
        
        logger.info(f"Initialized smart contract wrapper (min_clients={self.min_clients}) at {contract_address}")
    
    def register_client(
        self,
        client_address: str,
        organization: str,
        data_size: int,
        data_quality: float = 1.0
    ) -> bool:
        """
        Register a new client on the blockchain.
        
        Args:
            client_address: Ethereum address of the client
            organization: Organization name
            data_size: Dataset size
            data_quality: Data quality score (0-1)
            
        Returns:
            True if registration successful
        """
        # Convert float quality strictly back to uint256 scaled format (e.g. 0.95 -> 95)
        scaled_quality = int(data_quality * 100)
        
        try:
            receipt = self.eth.send_transaction(
                self.contract,
                'registerClient',
                self.admin_pk,
                client_address,
                organization,
                data_size,
                scaled_quality
            )
            logger.info(f"Registered client {client_address} ({organization}) in tx {receipt['transactionHash'].hex()}")
            return True
        except Exception as e:
            logger.warning(f"Failed to register client {client_address}: {str(e)}")
            return False
    
    def deactivate_client(self, client_address: str) -> bool:
        """Deactivate a client on the blockchain."""
        try:
            receipt = self.eth.send_transaction(
                self.contract,
                'deactivateClient',
                self.admin_pk,
                client_address
            )
            logger.info(f"Deactivated client {client_address} in tx {receipt['transactionHash'].hex()}")
            return True
        except Exception as e:
            logger.warning(f"Failed to deactivate client {client_address}: {str(e)}")
            return False
    
    def can_aggregate(self, participating_clients: List[str]) -> bool:
        """
        Check if aggregation can proceed via the smart contract constraint.
        
        Args:
            participating_clients: List of client Ethereum addresses
            
        Returns:
            True if aggregation allowed by contract
        """
        try:
            return self.eth.call_view_function(
                self.contract,
                'canAggregate',
                participating_clients
            )
        except Exception as e:
            logger.error(f"Error checking canAggregate: {str(e)}")
            return False
    
    def log_access(self, client_id: str, action: str, success: bool):
        """Log client access (Off-chain for cheap auditing)."""
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "action": action,
            "success": success
        })
    
    def get_client_info(self, client_address: str) -> Optional[Dict]:
        """Get client information from the blockchain."""
        try:
            client_data = self.eth.call_view_function(self.contract, 'clients', client_address)
            # Solidity struct returns a tuple based on the fields defined
            if client_data[0] == "": # organization is empty if uninitialized
                return None
                
            return {
                "organization": client_data[0],
                "data_size": client_data[1],
                "data_quality": client_data[2] / 100.0,
                "registered_at": client_data[3],
                "active": client_data[4]
            }
        except Exception as e:
            logger.error(f"Error fetching client info: {str(e)}")
            return None
    
    def get_active_clients(self) -> List[str]:
        """Get list of active client addresses from blockchain."""
        try:
            return self.eth.call_view_function(self.contract, 'getActiveClients')
        except Exception as e:
            logger.error(f"Error fetching active clients: {str(e)}")
            return []

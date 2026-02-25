// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MedChainGovernance
 * @notice Manages hospital client registration and access control for MedChain-FL.
 *
 * Security notes (vs. previous version):
 *  - Uses an EnumerableSet-style self-removing swap-and-pop pattern (already present).
 *  - Added MAX_CLIENTS guard to prevent unbounded activeClientAddresses array DoS.
 *  - Added input validation for organization string length and data quality range.
 *  - admin is set once in constructor; explicit transferAdmin pattern added.
 *  - All state-changing functions emit events for off-chain auditability.
 */
contract MedChainGovernance {
    address public admin;
    uint256 public minClients;
    uint256 public minDataQuality; // Scaled by 100 (e.g. 60 == 0.60)

    /// Maximum number of concurrently registered clients.
    /// Prevents unbounded-loop gas DoS attacks.
    uint256 public constant MAX_CLIENTS = 256;

    /// Maximum byte length of an organisation string.
    uint256 public constant MAX_ORG_LEN = 128;

    struct Client {
        string organization;
        uint256 dataSize;
        uint256 dataQuality;
        uint256 registeredAt;
        bool active;
    }

    mapping(address => Client) public clients;
    address[] public activeClientAddresses;

    event ClientRegistered(address indexed clientAddress, string organization);
    event ClientDeactivated(address indexed clientAddress);
    event GovernanceParamsUpdated(uint256 minClients, uint256 minDataQuality);
    event AdminTransferred(address indexed previousAdmin, address indexed newAdmin);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this");
        _;
    }

    constructor(uint256 _minClients, uint256 _minDataQuality) {
        require(_minDataQuality <= 100, "minDataQuality must be <= 100");
        admin = msg.sender;
        minClients = _minClients;
        minDataQuality = _minDataQuality;
    }

    // -------------------------------------------------------------------------
    // Admin management
    // -------------------------------------------------------------------------

    /// @notice Transfer admin role to a new address (e.g. multi-sig).
    function transferAdmin(address _newAdmin) external onlyAdmin {
        require(_newAdmin != address(0), "New admin cannot be zero address");
        emit AdminTransferred(admin, _newAdmin);
        admin = _newAdmin;
    }

    // -------------------------------------------------------------------------
    // Client management
    // -------------------------------------------------------------------------

    function registerClient(
        address _clientAddress,
        string memory _organization,
        uint256 _dataSize,
        uint256 _dataQuality
    ) external onlyAdmin {
        require(_clientAddress != address(0), "Client address cannot be zero");
        require(bytes(_organization).length > 0, "Organization name cannot be empty");
        require(bytes(_organization).length <= MAX_ORG_LEN, "Organization name too long");
        require(_dataQuality >= minDataQuality, "Data quality too low");
        require(_dataQuality <= 100, "Data quality cannot exceed 100");
        require(!clients[_clientAddress].active, "Client already registered and active");
        require(activeClientAddresses.length < MAX_CLIENTS, "Max client limit reached");

        clients[_clientAddress] = Client({
            organization: _organization,
            dataSize: _dataSize,
            dataQuality: _dataQuality,
            registeredAt: block.timestamp,
            active: true
        });

        // Check if address already exists in the list (re-registration after deactivation)
        bool exists = false;
        for (uint i = 0; i < activeClientAddresses.length; i++) {
            if (activeClientAddresses[i] == _clientAddress) {
                exists = true;
                break;
            }
        }
        if (!exists) {
            activeClientAddresses.push(_clientAddress);
        }

        emit ClientRegistered(_clientAddress, _organization);
    }

    function deactivateClient(address _clientAddress) external onlyAdmin {
        require(clients[_clientAddress].active, "Client is not active");
        clients[_clientAddress].active = false;

        // Swap-and-pop: O(1) removal, avoids shifting the array
        uint256 len = activeClientAddresses.length;
        for (uint i = 0; i < len; i++) {
            if (activeClientAddresses[i] == _clientAddress) {
                activeClientAddresses[i] = activeClientAddresses[len - 1];
                activeClientAddresses.pop();
                break;
            }
        }

        emit ClientDeactivated(_clientAddress);
    }

    // -------------------------------------------------------------------------
    // View functions
    // -------------------------------------------------------------------------

    function canAggregate(address[] calldata _participatingClients) external view returns (bool) {
        if (_participatingClients.length < minClients) {
            return false;
        }
        for (uint i = 0; i < _participatingClients.length; i++) {
            if (!clients[_participatingClients[i]].active) {
                return false;
            }
        }
        return true;
    }

    function getActiveClients() external view returns (address[] memory) {
        return activeClientAddresses;
    }

    // -------------------------------------------------------------------------
    // Parameter management
    // -------------------------------------------------------------------------

    function updateParams(uint256 _minClients, uint256 _minDataQuality) external onlyAdmin {
        require(_minDataQuality <= 100, "minDataQuality must be <= 100");
        minClients = _minClients;
        minDataQuality = _minDataQuality;
        emit GovernanceParamsUpdated(_minClients, _minDataQuality);
    }
}

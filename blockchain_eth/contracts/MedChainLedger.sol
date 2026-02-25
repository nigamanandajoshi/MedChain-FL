// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./MedChainGovernance.sol";

/**
 * @title MedChainLedger
 * @notice Immutable ledger for federated learning rounds and client updates.
 *
 * Security fixes vs. previous version:
 *  - Added MAX_METRICS_LEN and MAX_HASH_LEN to prevent gas-bomb attacks via
 *    arbitrarily large string arguments.
 *  - recordFLRound validates _round > 0 and that it has not already been recorded
 *    (prevents overwriting history).
 *  - recordClientUpdate validates _round > 0.
 */
contract MedChainLedger {
    address public admin;
    MedChainGovernance public governance;

    /// Maximum byte length of the JSON metrics blob stored on-chain.
    uint256 public constant MAX_METRICS_LEN = 4096;

    /// Maximum byte length of the model hash string (SHA-256 hex = 64 chars).
    uint256 public constant MAX_HASH_LEN = 128;

    struct ClientUpdate {
        address clientAddress;
        uint256 round;
        uint256 dataSize;
        string metricsJson;
        uint256 timestamp;
    }

    struct FLRound {
        uint256 round;
        uint256 numClients;
        string metricsJson;
        string modelHash;
        uint256 timestamp;
    }

    mapping(uint256 => FLRound) public flRounds;
    uint256 public latestRound;

    mapping(uint256 => ClientUpdate[]) public roundClientUpdates;

    event FLRoundRecorded(uint256 indexed round, uint256 numClients, string modelHash);
    event ClientUpdateRecorded(address indexed clientAddress, uint256 indexed round);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this");
        _;
    }

    modifier onlyActiveClient() {
        (, , , , bool active) = governance.clients(msg.sender);
        require(active, "Only active registered clients can log updates");
        _;
    }

    constructor(address _governanceAddress) {
        require(_governanceAddress != address(0), "Governance address cannot be zero");
        admin = msg.sender;
        governance = MedChainGovernance(_governanceAddress);
    }

    // -------------------------------------------------------------------------
    // Client update recording
    // -------------------------------------------------------------------------

    function recordClientUpdate(
        uint256 _round,
        uint256 _dataSize,
        string calldata _metricsJson
    ) external onlyActiveClient {
        require(_round > 0, "Round must be >= 1");
        require(bytes(_metricsJson).length <= MAX_METRICS_LEN, "Metrics JSON too large");

        roundClientUpdates[_round].push(ClientUpdate({
            clientAddress: msg.sender,
            round: _round,
            dataSize: _dataSize,
            metricsJson: _metricsJson,
            timestamp: block.timestamp
        }));

        emit ClientUpdateRecorded(msg.sender, _round);
    }

    // -------------------------------------------------------------------------
    // FL round recording
    // -------------------------------------------------------------------------

    function recordFLRound(
        uint256 _round,
        uint256 _numClients,
        string calldata _metricsJson,
        string calldata _modelHash
    ) external onlyAdmin {
        require(_round > 0, "Round must be >= 1");
        require(flRounds[_round].round == 0, "Round already recorded -- history is immutable");
        require(bytes(_metricsJson).length <= MAX_METRICS_LEN, "Metrics JSON too large");
        require(bytes(_modelHash).length <= MAX_HASH_LEN, "Model hash too long");
        require(
            roundClientUpdates[_round].length >= _numClients,
            "Not enough client updates logged for this round"
        );

        flRounds[_round] = FLRound({
            round: _round,
            numClients: _numClients,
            metricsJson: _metricsJson,
            modelHash: _modelHash,
            timestamp: block.timestamp
        });

        if (_round > latestRound) {
            latestRound = _round;
        }

        emit FLRoundRecorded(_round, _numClients, _modelHash);
    }

    // -------------------------------------------------------------------------
    // View functions
    // -------------------------------------------------------------------------

    function getClientUpdates(uint256 _round) external view returns (ClientUpdate[] memory) {
        return roundClientUpdates[_round];
    }
}

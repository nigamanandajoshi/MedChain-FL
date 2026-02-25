import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("MedChainModule", (m) => {
  // Deploy Governance first with default params (minClients = 2, minDataQuality = 60/100)
  const governance = m.contract("MedChainGovernance", [2, 60]);

  // Deploy Ledger and pass the Governance contract address to its constructor
  const ledger = m.contract("MedChainLedger", [governance]);

  return { governance, ledger };
});

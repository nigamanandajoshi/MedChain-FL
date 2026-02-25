import hre from "hardhat";
import fs from "fs";

async function main() {
    console.log("Deploying MedChain Governance...");
    const Governance = await hre.ethers.getContractFactory("MedChainGovernance");
    const governance = await Governance.deploy(2, 60);
    await governance.waitForDeployment();

    const govAddress = await governance.getAddress();
    console.log("Governance deployed to:", govAddress);

    console.log("Deploying MedChain Ledger...");
    const Ledger = await hre.ethers.getContractFactory("MedChainLedger");
    const ledger = await Ledger.deploy(govAddress);
    await ledger.waitForDeployment();

    const ledgerAddress = await ledger.getAddress();
    console.log("Ledger deployed to:", ledgerAddress);

    // Write addresses to config file for python tests
    const config = {
        governance: govAddress,
        ledger: ledgerAddress
    };

    fs.writeFileSync("../contract_addresses.json", JSON.stringify(config, null, 2));
    console.log("Addresses saved to ../contract_addresses.json");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

from web3 import Web3
import json
import os
from typing import Optional, Dict, List

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        self.contract = None
        self.contract_address = None
        self.accounts = []

        if self.w3.is_connected():
            self.accounts = self.w3.eth.accounts
            print("✅ Connected to Ganache")
        else:
            print("❌ Failed to connect to Ganache")

    def get_funded_account(self, preferred_account: str = None) -> str:
        """Always return a funded account for transactions"""
        if preferred_account and preferred_account in self.accounts:
            balance = self.w3.eth.get_balance(preferred_account)
            if balance > 0:
                return preferred_account
        # Fallback to first account which always has funds
        return self.accounts[0] if self.accounts else None

    def load_contract(self, contract_path: str = None):
        if contract_path is None:
            contract_path = "../blockchain/build/contracts/CertificateAuthentication.json"

        try:
            with open(contract_path, 'r') as file:
                contract_json = json.load(file)
                contract_abi = contract_json['abi']

                network_id = str(self.w3.eth.chain_id)

                if network_id not in contract_json['networks']:
                    if "1337" in contract_json['networks']:
                        network_id = "1337"

                if network_id in contract_json['networks']:
                    self.contract_address = contract_json['networks'][network_id]['address']
                else:
                    found_address = None
                    for net_id, net_info in contract_json['networks'].items():
                        if 'address' in net_info:
                            found_address = net_info['address']
                            break

                    if found_address:
                        self.contract_address = found_address
                    else:
                        print("❌ No deployed contract address found in JSON for any network.")
                        return False

                self.contract = self.w3.eth.contract(
                    address=self.contract_address,
                    abi=contract_abi
                )
                print(f"✅ Contract loaded at {self.contract_address}")
                return True
        except Exception as e:
            print(f"❌ Error loading contract: {str(e)}")
            return False

    def issue_certificate(self, certificate_id: str, certificate_type: str,
                         holder_name: str, institution_name: str,
                         qualification_name: str, image_hash: str,
                         expiry_timestamp: int, from_account: str) -> Optional[str]:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            sender = self.get_funded_account(from_account)

            tx_hash = self.contract.functions.issueCertificate(
                certificate_id, certificate_type, holder_name,
                institution_name, qualification_name, image_hash, expiry_timestamp
            ).transact({'from': sender, 'gas': 3000000})

            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_hash.hex()
        except Exception as e:
            print(f"Error issuing certificate: {str(e)}")
            return None

    def link_qr_code(self, certificate_id: str, qr_hash: str, from_account: str) -> bool:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            sender = self.get_funded_account(from_account)

            tx_hash = self.contract.functions.linkQRCode(
                certificate_id, qr_hash
            ).transact({'from': sender, 'gas': 300000})

            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return True
        except Exception as e:
            print(f"Error linking QR code: {str(e)}")
            return False

    def transfer_certificate(self, certificate_id: str, new_holder: str, from_account: str) -> bool:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            sender = self.get_funded_account(from_account)

            tx_hash = self.contract.functions.transferCertificate(
                certificate_id, new_holder
            ).transact({'from': sender, 'gas': 300000})

            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return True
        except Exception as e:
            print(f"Error transferring certificate: {str(e)}")
            return False

    def revoke_certificate(self, certificate_id: str, from_account: str) -> bool:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            sender = self.get_funded_account(from_account)

            tx_hash = self.contract.functions.revokeCertificate(
                certificate_id
            ).transact({'from': sender, 'gas': 300000})

            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return True
        except Exception as e:
            print(f"Error revoking certificate: {str(e)}")
            return False

    def verify_certificate(self, certificate_id: str, from_account: str) -> Dict:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            sender = self.get_funded_account(from_account)

            is_valid = self.contract.functions.verifyCertificate(
                certificate_id
            ).call({'from': sender})

            certificate_details = self.get_certificate(certificate_id)
            transfer_history = self.get_transfer_history(certificate_id)

            return {
                "is_valid": is_valid,
                "is_revoked": certificate_details.get("is_revoked", False),
                "certificate": certificate_details,
                "lifecycle": transfer_history
            }
        except Exception as e:
            print(f"Error verifying certificate: {str(e)}")
            return {"is_valid": False, "error": str(e)}

    def verify_by_qr(self, qr_hash: str, from_account: str) -> Dict:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            sender = self.get_funded_account(from_account)

            result = self.contract.functions.verifyByQRCode(
                qr_hash
            ).call({'from': sender})

            is_valid, certificate_id = result
            certificate_details = self.get_certificate(certificate_id)
            transfer_history = self.get_transfer_history(certificate_id)

            return {
                "is_valid": is_valid,
                "certificate_id": certificate_id,
                "is_revoked": certificate_details.get("is_revoked", False),
                "certificate": certificate_details,
                "lifecycle": transfer_history
            }
        except Exception as e:
            print(f"Error verifying by QR: {str(e)}")
            return {"is_valid": False, "error": str(e)}

    def get_certificate(self, certificate_id: str) -> Dict:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            result = self.contract.functions.getCertificate(certificate_id).call()

            return {
                "certificate_id": result[0],
                "certificate_type": result[1],
                "holder_name": result[2],
                "institution_name": result[3],
                "qualification_name": result[4],
                "image_hash": result[5],
                "issuer": result[6],
                "current_holder": result[7],
                "issued_at": result[8],
                "expiry_date": result[9],
                "is_valid": result[10],
                "is_revoked": result[11]
            }
        except Exception as e:
            print(f"Error getting certificate: {str(e)}")
            return {}

    def get_transfer_history(self, certificate_id: str) -> List[Dict]:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            transfers = self.contract.functions.getTransferHistory(certificate_id).call()

            history = []
            for transfer in transfers:
                history.append({
                    "from": transfer[0],
                    "to": transfer[1],
                    "timestamp": transfer[2],
                    "transfer_type": transfer[3]
                })

            return history
        except Exception as e:
            print(f"Error getting transfer history: {str(e)}")
            return []

    def authorize_issuer(self, issuer_address: str, from_account: str) -> bool:
        try:
            if not self.contract:
                raise Exception("Contract not loaded")

            sender = self.get_funded_account(from_account)

            tx_hash = self.contract.functions.authorizeIssuer(
                issuer_address
            ).transact({'from': sender, 'gas': 300000})

            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return True
        except Exception as e:
            print(f"Error authorizing issuer: {str(e)}")
            return False

blockchain_service = BlockchainService()
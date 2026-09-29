from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
if w3.is_connected():
    print(f"Connected to Ganache. Chain ID: {w3.eth.chain_id}")
    try:
        with open('../blockchain/build/contracts/CertificateAuthentication.json', 'r') as f:
            data = json.load(f)
            networks = data.get('networks', {})
            print(f"Networks in JSON: {list(networks.keys())}")
            
            if str(w3.eth.chain_id) in networks:
                print(f"Match found! Address: {networks[str(w3.eth.chain_id)]['address']}")
            else:
                print("No match found for current Chain ID in JSON networks.")
    except FileNotFoundError:
        print("CertificateAuthentication.json not found.")
else:
    print("Failed to connect to Ganache")

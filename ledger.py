import hashlib
import json
import os
from time import time

DB_FILE = "chain_db.json"

class SatyaLedger:
    def __init__(self):
        self.chain = []
        
        # 1. Try to load existing database
        if os.path.exists(DB_FILE):
            self.load_chain()
        
        # 2. If database is empty/missing, create Genesis Block
        if len(self.chain) == 0:
            self.create_block(previous_hash='1', proof=100)

    def create_block(self, proof, previous_hash=None, data=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'data': data or "Genesis Block - SatyaChain Initialized"
        }
        
        self.chain.append(block)
        
        # 3. SAVE TO DATABASE IMMEDIATELY
        self.save_chain()
        
        return block

    @staticmethod
    def hash(block):
        # Sort keys to ensure consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # --- DATABASE FUNCTIONS ---
    def save_chain(self):
        """Saves the current chain to a local JSON file."""
        try:
            with open(DB_FILE, 'w') as f:
                json.dump(self.chain, f, indent=4)
            print(f"💾 Blockchain saved to {DB_FILE}")
        except Exception as e:
            print(f"❌ Error saving database: {e}")

    def load_chain(self):
        """Loads the chain from the local JSON file."""
        try:
            with open(DB_FILE, 'r') as f:
                self.chain = json.load(f)
            print(f"📂 Loaded {len(self.chain)} blocks from database.")
        except Exception as e:
            print(f"⚠️ Could not load database: {e}. Starting fresh.")
            self.chain = []
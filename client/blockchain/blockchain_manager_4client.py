# coding: utf-8

import threading
import hashlib
import json
import binascii
import copy

class BlockchainManager:
    def __init__(self, genesis_block):
        print("Initializing BlockchainManager...")
        self.chain = []
        self.lock = threading.Lock()
        self.__set_gblock(genesis_block)

    def __set_gblock(self, genesis_block):
        self.genesis_block = genesis_block
        self.chain.append(genesis_block)

    def set_new_block(self, block):
        with self.lock:
            self.chain.append(block)

    def get_my_blockchain(self):
        if len(self.chain) > 1:
            print("My blockchain is...")
            print(json.dumps(self.chain, indent = 4))
        else:
            return

    def get_txs(self):
        # get all txs from blockchain
        print("get_txs was called")
        current_index = 1
        txs = []
        while current_index < len(self.chain):
            block = self.chain[current_index]
            transactions = block["transactions"]
            for t in transactions:
                txs.append(t)
            current_index += 1
        return txs

    def get_hash(self, block):
        print("get_hash was called")
        block_string = json.dumps(block, sort_keys = True)
        return binascii.hexlify(self.double_hash((block_string).encode())).decode("ascii")

    def double_hash(self, message):
        return hashlib.sha256(hashlib.sha256(message).digest()).digest()

    def resolve_conflicts(self, chain):
        mychain_len = len(self.chain)
        newchain_len = len(chain)
        pool_4_orphan_blocks = copy.deepcopy(self.chain)
        has_orphan = False

        if newchain_len > mychain_len:
            for b in pool_4_orphan_blocks:
                for b2 in chain:
                    if b == b2:
                        pool_4_orphan_blocks.remove(b)
            result = self.renew_my_blockchain(chain)
            if result is not None:
                return result, pool_4_orphan_blocks
            else:
                return None, []
        else:
            print("invalid cahin cannot be set...")
            return None, []

    def is_valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if self.is_valid_block(self.get_hash(last_block), block) is not True:
                return False
            last_block = chain[current_index]
            current_index += 1
        return True

    def is_valid_block(self, previous_hash, block, difficulty = 5):
        # Verification of Block
        suffix = "0" * difficulty
        block_4_pow = copy.deepcopy(block)
        nonce = block_4_pow["nonce"]
        del block_4_pow["nonce"]

        message = json.dumps(block_4_pow, sort_keys = True)
        nonce = str(nonce)

        if block["previous_hash"] != previous_hash:
            print("Invalid block (bad previous_hash)")
            return False
        else:
            digest = binascii.hexlify(self.double_hash((message + nonce).encode())).decode("ascii")
            if digest.startswith(suffix):
                print("OK, this seems valid block")
                return True
            else:
                print("Invalid block (nonce)")
                return False

    def renew_my_blockchain(self, blockchain):
        print("renew_my_blockchain was called")
        with self.lock:
            if self.is_valid_chain(blockchain):
                self.chain = blockchain
                latest_block = self.chain[-1]
                return self.get_hash(latest_block)
            else:
                print("invalid chain cannot be set...")
                return None

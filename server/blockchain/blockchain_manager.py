# coding: utf-8

import threading
import hashlib
import json
import binascii
import copy

class BlockchainManager:
    def __init__(self, genesis_block):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nInitializing BlockchainManager...")
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
            return self.chain
        else:
            return None

    def get_my_chain_length(self):
        return len(self.chain)

    def double_hash(self, message):
        return hashlib.sha256(hashlib.sha256(message).digest()).digest()

    def get_hash(self, block):
        block_string = json.dumps(block, sort_keys = True)
        return binascii.hexlify(self.double_hash((block_string).encode())).decode("ascii")

    def is_valid(self, chain):
        # Verification of Blockchain
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = self.chain[current_index]
            if block["previous_hash"] != self.get_hash(last_block):
                return False

            last_block = block
            current_index += 1
        return True

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
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nInvalid block (bad previous_hash)")
            return False
        else:
            digest = binascii.hexlify(self.double_hash((message + nonce).encode())).decode("ascii")
            if digest.startswith(suffix):
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nOK, this seems valid block")
                return True
            else:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nInvalid block (nonce)")
                return False

    def remove_used_tx(self, transaction_pool):
        if len(transaction_pool) != 0:
            current_index = 1
            while current_index < len(self.chain):
                block = self.chain[current_index]
                transactions = block["transactions"]
                for t in transactions:
                    for t2 in transaction_pool:
                        if t == t2:
                            with open("/usr/local/server/log.txt", "a") as f:
                                f.write("\nalready exist in my blockchain: {0}".format(t2))
                            transaction_pool.remove(t2)
                current_index += 1
            return transaction_pool
        else:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nno transaction to be removes...")
            return[]

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
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\ninvalid cahin cannot be set...")
            return None, []

    def renew_my_blockchain(self, blockchain):
        with open("usr/local/server/log.txt", "a") as f:
            f.write("\nrenew_my_blockchain was called")
        with self.lock:
            if self.is_valid_chain(blockchain):
                self.chain = blockchain
                latest_block = self.chain[-1]
                return self.get_hash(latest_block)
            else:
                with open("usr/local/server/log.txt", "a") as f:
                    f.write("\ninvalid chain cannot be set...")
                return None

    def has_this_output_in_my_chain(self, transaction_output):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nhas_this_output_in_my_chain was called")
        current_index = 1
        if len(self.chain) == 1:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nonly the genesis_block is my chain")
            return False
        while current_index < len(self.chain):
            block = self.chain[current_index]
            transactions = block["transactions"]

            for t in transactions:
                if t["t_type"] == "basic" or "coinbase_transaction":
                    if t["inputs"] != []:
                        inputs_t = t["inputs"]
                        for it in inputs_t:
                            if it["transaction"]["outputs"][it["output_index"]] == transaction_output:
                                with open("/usr/local/server/log.txt", "a") as f:
                                    f.write("\nthis Transaction was already used")
                                return True
            current_index += 1
        return False

    def is_valid_output_in_my_chain(self, transaction_output):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nis_valid_output_in_my_chain was called")
        current_index = 1
        while current_index < len(self.chain):
            block = self.chain[current_index]
            transactions = block["transactions"]
            for t in transactions:
                if t["t_type"] == "basic" or "coinbase_transaction":
                    outputs_t = t["outputs"]
                    for ot in outputs_t:
                        if ot == transaction_output:
                            return True
            current_index += 1
        return False

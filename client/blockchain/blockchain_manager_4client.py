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
            print(self.chain)
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
                txs.append(json.loads(t))
            current_index += 1
        return txs

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

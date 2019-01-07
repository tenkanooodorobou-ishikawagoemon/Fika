# coding: utf-8
import json
import hashlib
import binascii
from datetime import datetime
from time import time

class Block:
    def __init__(self, transaction, previous_hash):
        self.timestamp = time()
        self.transaction = transaction
        self.previous_hash = previous_hash
        time1 = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        json_block = json.dumps(self.to_dict(nonce = False), sort_keys = True)
        self.nonce = self.pow(json_block)
        time2 = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print("{0} -> {1}".format(time1, time2))

    def to_dict(self, nonce = True):
        d = {
        "timestamp": self.timestamp,
        "transaction": json.dumps(self.transaction),
        "previous_hash": self.previous_hash,
        }
        if nonce:
            d["nonce"] = self.nonce
        return d

    def pow(self, message, difficulty = 5):
        i = 0
        suffix = "0" * difficulty
        while True:
            nonce = str(i)
            digest = binascii.hexlify(self.double_hash((message + nonce).encode())).decode("ascii")
            if digest.startswith(suffix):
                return nonce
            i += 1

    def double_hash(self, message):
        return hashlib.sha256(hashlib.sha256(message).digest()).digest()

class GenesisBlock(Block):
    def __init__(self):
        ###
        #88b862be658241b71aef4dc6684cd3f6701da949e503c1c40aa82e37ade76a4e is sha256('fika')
        ###
        super().__init__(transaction = "88b862be658241b71aef4dc6684cd3f6701da949e503c1c40aa82e37ade76a4e", previous_hash = None)

    def to_dict(self, nonce = True):
        d = {
        "transaction": self.transaction,
        "genesis_block": True,
        }
        if nonce:
            d["nonce"] = self.nonce
        return d

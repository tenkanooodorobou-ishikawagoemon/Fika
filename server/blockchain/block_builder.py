# coding: utf-8

from blockchain.block import *

class BlockBuilder:
    def __init__(self):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nInitializing BlockBuilder...")

    def generate_genesis_block(self):
        genesis_block = GenesisBlock()
        return genesis_block

    def generate_new_block(self, transaction, previous_hash):
        new_block = Block(transaction, previous_hash)
        return new_block

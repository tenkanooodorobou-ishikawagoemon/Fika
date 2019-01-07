# coding: utf-8

from time import time

class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = time()
        self.tx_type = "basic"

class TransactionInput:
    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index

    def to_dict(self):
        d = {
        "transaction": self.transaction,
        "output_index": self.output_index
        }
        return d

class TransactionOutput:
    def __init__(self, recipient_address, value):
        self.recipient = recipient_address
        self.value = value

    def to_dict(self):
        d = {
        "recipient": self.recipient,
        "value": self.value
        }
        return d

class CoinbaseTransaction(Transaction):
    def __init__(self, recipient_address, value = 30):
        pass

    def to_dict(self):
        pass

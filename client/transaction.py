# coding: utf-8
from time import time

class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = time()
        self.t_type = "basic"

    def to_dict(self):
        d = {
        "inputs": list(map(TransactionInput.to_dict, self.inputs)),
        "outputs": list(map(TransactionOutput.to_dict, self.outputs)),
        "timestamp": self.timestamp,
        "t_type": self.t_type
        }
        return d

    def compute_change(self, fee):
        total_in = sum(i.transaction["outputs"][i.output_index]["value"] for i in self.inputs)
        total_out = sum(int(o.value) for o in self.outputs) + int(fee)
        delta = total_in - total_out
        return delta

    def is_enough_inputs(self, fee = 0):
        total_in = sum(i.transaction["outputs"][i.output_index]["value"] for i in self.inputs)
        total_out = sum(int(o.value) for o in self.outputs) + int(fee)

        delta = total_in - total_out
        if delta >= 0:
            return True
        else:
            return False


class TransactionOutput:
    def __init__(self, recipient_address, value):
        self.recipient = recipient_address
        self.value = value

    def to_dict(self):
        d = {
        "recipient": self.recipient,
        "value": self.value,
        }
        return d

class TransactionInput:
    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index

    def to_dict(self):
        d = {
        "transaction": self.transaction,
        "output_index": self.output_index,
        }
        return d

class CoinbaseTransaction(Transaction):
    def __init__(self, recipient_address, value = 30):
        self.inputs = []
        self.outputs = [TransactionOutput(recipient_address, value)]
        self.timestamp = time()
        self.t_type = "coinbase_transaction"

    def to_dict(self):
        d = {
        "inputs": [],
        "outputs": list(map(TransactionOutput.to_dict, self.outputs)),
        "timestamp": self.timestamp,
        "t_type": self.t_type,
        }
        return d

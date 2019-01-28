# coding: utf-8

import threading

class TransactionPool:
    def __init__(self):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nInitializing TransactionPool...")
        self.transactions = []
        self.lock = threading.Lock()

    def set_new_transaction(self, transaction):
        with self.lock:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nset_new_transaction was called\n{0}".format(transaction))
            self.transactions.append(transaction)

    def clear_my_transactions(self, index):
        with self.lock:
            if index <= len(self.transactions):
                new_transactions = self.transactions
                del new_transactions[0:index]
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\ntransaction is now refreshed...")
                self.transactions = new_transactions

    def get_stored_transactions(self):
        if len(self.transactions) > 0:
            return self.transactions
        else:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nCurrently, it seems transaction pool is empty...")
            return []

    def get_total_fee_from_tp(self):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nget_total_fee_from_tp was called")
        transactions = self.transactions
        result = 0
        for t in transactions:
            checked = self.check_type_of_transaction(t)
            if checked:
                total_in = sum(i["transaction"]["outputs"][i["output_index"]]["value"] for i in t["inputs"])
                total_out = sum(o["value"] for o in t["outputs"])
                delta = total_in - total_out
                result += delta
        return result

    def check_type_of_transaction(self, transaction):
        if transaction["t_type"] == "basic" or transaction["t_type"] == "coinbase_transaction":
            return True
        else:
            return False

    def renew_my_transactions(self, transactions):
        with self.lock:
            self.transactions = transactions
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\ntransaction pool will be renewed...")

    def has_this_output_in_my_tp(self, transaction_output):
        with open("/usr/local/server/log.txt", "a") as f:
            print("\nhas_this_output_in_my_tp was called")
        transactions = self.transactions
        for t in transactions:
            inputs_t = t["inputs"]
            for it in inputs_t:
                if it == transaction_output:
                    return True

        return False

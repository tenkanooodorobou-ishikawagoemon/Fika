# coding: utf-8

class UTXOManager:
    def __init__(self, address):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nInitializing UTXOManager...")
        self.my_address = address
        self.utxo_txs = []
        self.my_balance = 0

    def extract_utxos(self, txs):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nextract_utxos called!")
        outputs = []
        inputs = []
        idx = 0
        for t in txs:
            result, t_type = self.check_tx_type(t)
            if result is not True:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nthis is not fikacoin tx")
                continue
            for txout in t["outputs"]:
                recipient = txout["recipient"]
                if recipient == self.my_address:
                    outputs.append(t)
            for txin in t["inputs"]:
                t_in_txin = txin["transaction"]
                idx = txin["output_index"]
                o_recipient = t_in_txin["outputs"][idx]["recipient"]
                if o_recipient == self.my_address:
                    inputs.append(t)
        if outputs is not []:
            for o in outputs:
                if inputs is not []:
                    for i in inputs:
                        for i_i in i["inputs"]:
                            if o == i_i["transaction"]:
                                outputs.remove(o)
                else:
                    break
        else:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nNo Transaction for UTXO")
            return
        print(outputs)
        self._set_my_utxo_txs(outputs)

    def _set_my_utxo_txs(self, txs):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\n_set_my_utxo_txs was called\n")
            f.write(txs)
        self.utxo_txs = []
        for t in txs:
            self.put_utxo_tx(t)

    def put_utxo_tx(self, tx):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("put_utxo_tx was called")
        idx = 0
        for txout in tx["outputs"]:
            if txout["recipient"] == self.my_address:
                self.utxo_txs.append((tx, idx))
            else:
                idx += 1
        self._compute_my_balance()

    def get_utxo_tx(self, idx):
        return self.utxo_txs[idx]

    def remove_utxo_txs(self, tx):
        self.utxo_txs.remove(tx)
        self._compute_my_balance()

    def _compute_my_balance(self):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("_compute_my_balance was called")
        balance = 0
        txs = self.utxo_txs
        for t in txs:
            for txout in t[0]["outputs"]:
                print("txout", txout)
                if txout["recipient"] == self.my_address:
                    balance += txout["value"]
        self.my_balance = balance

    def check_tx_type(self, tx):
        tx_t = tx["t_type"]
        t_basic = "basic"
        t_coinbase = "coinbase_transaction"
        unknown = "unknown"
        if tx_t != t_basic:
            if tx_t != t_coinbase:
                return False, unknown
            else:
                return True, t_coinbase
        else:
            return True, t_basic

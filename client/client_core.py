# coding: utf-8
import sys
import json
import socket
import pickle
import subprocess
from time import sleep

from keymanager import KeyManager
from transaction.utxo_manager import UTXOManager
from transaction.transactions import *
from blockchain.block_builder import BlockBuilder
from blockchain.blockchain_manager_4client import BlockchainManager
from connection_manager_4client import ConnectionManager4Client
from message_manager import (
    MessageManager,
    MSG_NEW_TRANSACTION,
    MSG_REQUEST_FULL_CHAIN,
    RSP_FULL_CHAIN,
    MSG_REQUEST_LOG,
    RSP_LOG,
)

class ClientCore:
    def __init__(self):
        arg = "uname -n".split()
        self.name = subprocess.check_output(arg).decode().replace("\n", "")
        print("Initializing {0}...".format(self.name))
        self.cm = ConnectionManager4Client(self.name, self.__handle_message)
        self.cm.start()

        self.bb = BlockBuilder()
        genesis_block = self.bb.generate_genesis_block()
        self.bm = BlockchainManager(genesis_block.to_dict())
        self.km = KeyManager(self.name)
        self.um = UTXOManager(self.km.my_address())
        with open("/usr/local/client/key_list.txt", "r")as f:
            self.key_list = json.loads(f.read())

        #This is test
        t1 = CoinbaseTransaction(self.km.my_address())
        t2 = CoinbaseTransaction(self.km.my_address())
        t3 = CoinbaseTransaction(self.km.my_address())
        transactions = []
        transactions.append(t1.to_dict())
        transactions.append(t2.to_dict())
        transactions.append(t3.to_dict())
        self.um.extract_utxos(transactions)

    def make_transaction(self):
        while True:
            print("Please enter the recipient")
            print("If you finish this mode, enter command 'exit'")
            print(self.key_list.keys())
            recipient = input(">>>")
            if recipient in self.key_list.keys():
                recipientKey = self.key_list[recipient]
                break
            elif recipient == "exit":
                return
            else:
                print("Unknown recipient")
                continue
        print("How many coins do you want to send?")
        value = int(input(">>>"))
        print("Please configure the Tx's fee")
        fee = int(input(">>>"))
        utxo, idx = self.um.get_utxo_tx(0)
        t = Transaction(
        [TransactionInput(utxo, idx)],
        [TransactionOutput(recipientKey, value)]
        )
        counter = 1
        while t.is_enough_inputs(fee) is not True:
            new_utxo, new_idx = self.um.get_utxo_tx(counter)
            t.inputs.append(TransactionInput(new_utxo, new_idx))
            counter += 1
            if counter > len(self.um.utxo_txs):
                print("Not enough UTXO, so can't send Tx")
                break
        if t.is_enough_inputs(fee) is True:
            change = t.compute_change(fee)
            t.outputs.append(TransactionOutput(self.km.my_address(), change))
            to_be_signed = json.dumps(t.to_dict(), sort_keys = True)
            signed = self.km.compute_digital_signature(to_be_signed)
            new_tx = json.loads(to_be_signed)
            new_tx["signature"] = signed
            tx = json.dumps(new_tx)
            peer, msg = self.cm.get_message_text(MSG_NEW_TRANSACTION, tx)
            self.cm.send_msg(peer, msg)
            self.um.put_utxo_tx(t.to_dict())
            to_be_deleted = 0
            del_list = []
            while to_be_deleted < counter:
                del_tx = self.um.get_utxo_tx(to_be_deleted)
                del_list.append(del_tx)
                to_be_deleted += 1
            for dx in del_list:
                self.um.remove_utxo_txs(dx)

    def update_balance(self):
        return self.um.get_balance()

    def log(self):
        print("MSG_REQUEST_LOG is sending")
        peer, msg = self.cm.get_message_text(MSG_REQUEST_LOG)
        self.cm.send_msg(peer, msg)

    def update_chain(self):
        print("update my blockchain")
        peer, msg = self.cm.get_message_text(MSG_REQUEST_FULL_CHAIN)
        self.cm.send_msg(peer, msg)

    def get_my_blockchain(self):
        self.bm.get_my_blockchain()

    def __handle_message(self, msg):
        # msg -> [result, sender, reason, cmd, payload]
        if msg[3] == RSP_FULL_CHAIN:
            new_blockchain = json.loads(msg[4])
            print(json.dumps(new_blockchain, indent = 4))
            if msg[4] is not None:
                result, pool_4_orphan_blocks = self.bm.resolve_conflicts(new_blockchain)
                if result is not None:
                    self.previous_hash = result
                else:
                    print("Received blockchain is useless...")
            else:
                print("payload is None...")

        elif msg[3] == RSP_LOG:
            print("Server's log: \n", msg[4])

        else:
            print("Unknown command")

    def update_callback(self):
        print("update_callback was called")
        s_transactions = self.bm.get_txs()
        self.um.extract_utxos(s_transactions)
        return self.update_balance()


def main():
    client = ClientCore()
    balance = client.update_balance()
    cmd_list = ["exit", "tx", "log", "upbc", "chain"]
    while True:
        print("\nPlease enter the 'command' following down")
        print("""
'exit': stop this client node
'tx': make transaction
'log': show server's log connected with this node
'upbc': update my blockchain
'chain': show blockchain this node has""")
        print("My Balance is: {0}".format(balance))
        cmd = input(">>>: ")
        if cmd in cmd_list:
            if cmd == "exit":
                print("EXIT!!")
                sys.exit()
            elif cmd == "tx":
                client.make_transaction()
                balance = client.update_balance()
                continue
            elif cmd == "log":
                client.log()
                continue
            elif cmd == "upbc":
                client.update_chain()
                sleep(1)
                balance = client.update_callback()
                continue
            elif cmd == "chain":
                client.get_my_blockchain()
                continue
        else:
            print("Unknown command")
            continue

if __name__ == "__main__":
    main()

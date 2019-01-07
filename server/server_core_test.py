# coding: utf-8
import time
import socket
import subprocess
import threading
import json
import pickle
import copy
from time import sleep

from connection_manager import ConnectionManager
from transaction.utxo_manager import UTXOManager
from message_manager import (
    MessageManager,
    MSG_NEW_TRANSACTION,
    MSG_NEW_BLOCK,
    MSG_REQUEST_FULL_CHAIN,
    RSP_FULL_CHAIN,
    MSG_TEST,
)

class ServerCore:
    def __init__(self):
        arg = "uname -n".split()
        self.name = subprocess.check_output(arg).decode().replace("\n", "")
        with open("/usr/local/server/log.txt", "w") as f:
            f.write("Initializing {0}...".format(self.name))
        self.cm = ConnectionManager(self.name, self.__handle_message)
        self.cm.start()

        #self.flag_stop_block_build = False
        #self.bb_running = False
        #self.km = KeyManager()
        #self.um = UTXOManager(self.km.my_address())

    def __handle_message(self, msg):
        if msg[3] == MSG_NEW_TRANSACTION:
            new_transaction = json.loads(msg[4])
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nReceived new_transaction")
            t_type = self.um.check_tx_type(new_transaction)
            current_transactions = self.tp.get_stored_transactions()
            if new_transaction in current_transactions:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nThis is already pooled transaction")
                return
                if self.bm.get_my_chain_length() != 1:
                    checked = self._check_availability_of_transaction(new_transaction)
                    if not checked:
                        with open("/usr/local/server/log.txt", "a") as f:
                            f.write("\nTransaction Verification Error")
                        return
                self.tp.set_new_transaction(new_transaction)

                ###
                # send all server without sender
                ###
            else:
                if self.bm.get_my_chain_length() !=1:
                    checked = self._check_availability_of_transaction(new_transaction)
                    if not checked:
                        with open("/usr/local/server/log.txt", "a") as f:
                            f.write("\nTransaction Verification Error")
                        return
                self.tp.set_new_transaction(new_transaction)
                ###
                # send all server without sender
                ###

        elif msg[3] == MSG_NEW_BLOCK:
            new_block = json.loads(msg[4])
            if self.bm.is_valid_block(self.previous_hash, new_block):
                if self.bb_running:
                    self.flag_stop_block_build = True
                self.previous_hash = self.bm.get_hash(new_block)
                result = self.tp.get_stored_transactions()
                new_tp = self.bm.remove_useless_transaction(result)
                self.tp.renew_my_transactions(new_tp)
            else:
                self.get_all_chains_for_resolve_conflict()

        elif msg[3] == RSP_FULL_CHAIN:
            new_blockchain = pickle.loads(msg[4].encode())
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nnew_blockchain")
            result, pool_4_orphan_blocks = self.bm.resolve_conflicts(new_blockchain)
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nblockchain received from central")
            if result is not None:
                self.previous_hash = result
                if len(pool_4_orphan_blocks) != 0:
                    new_transactions = self.bm.get_transactions_from_orphan_blocks(pool_4_orphan_blocks)
                for t in new_transactions:
                    self.tp.set_new_transaction(t)
            else:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nReceived blockchain in useless...")

        elif msg[3] == MSG_TEST:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nServerCore received test message")

    def test_msg(self):
        peer, msg = self.cm.get_message_text_test("server1", MSG_TEST, "testing now")
        self.cm.send_msg(peer, msg)


server = ServerCore()
sleep(5)
server.test_msg()

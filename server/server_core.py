# coding: utf-8
import re
import time
import socket
import subprocess
import threading
import json
import pickle
import copy

from connection_manager import ConnectionManager
from transaction.utxo_manager import UTXOManager
from transaction.transactions import *
from blockchain.block_builder import BlockBuilder
from rsa_utils import RSAutil
from keymanager import KeyManager
from blockchain.blockchain_manager import BlockchainManager
from blockchain.transaction_pool import TransactionPool
from message_manager import (
    MessageManager,
    MSG_NEW_TRANSACTION,
    MSG_NEW_BLOCK,
    MSG_REQUEST_FULL_CHAIN,
    RSP_FULL_CHAIN,
    MSG_TEST,
)

CHECK_INTERVAL = 30

class ServerCore:
    def __init__(self):
        arg = "uname -n".split()
        self.name = subprocess.check_output(arg).decode().replace("\n", "")
        with open("/usr/local/server/log.txt", "w") as f:
            f.write("Initializing {0}...".format(self.name))
        self.cm = ConnectionManager(self.name, self.__handle_message)
        self.cm.start()
        self.bb = BlockBuilder()
        self.flag_stop_block_build = False
        self.is_bb_running = False
        my_genesis_block = self.bb.generate_genesis_block()
        self.bm = BlockchainManager(my_genesis_block.to_dict())
        self.previous_hash = self.bm.get_hash(my_genesis_block.to_dict())
        self.tp = TransactionPool()

        self.flag_stop_block_build = False
        self.bb_running = False
        self.km = KeyManager(self.name)
        self.um = UTXOManager(self.km.my_address())
        self.rsa_utils = RSAutil()
        self.start_block_building()

    def start_block_building(self):
        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def double_spending(self, transaction):
        v_result, used_outputs = self.rsa_util.verify_sbc_transaction_sig(transaction)
        if v_result is not True:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nsignature verification error on new transaction")
            return False
        for used_o in used_outputs:
            bm_v_result = self.bm.has_this_output_in_my_chain(used_o)
            tp_v_result = self.tp.has_this_output_in_my_tp(used_o)
            bm_v_result2 = self.bm.is_valid_output_in_my_chain(used_o)
            if bm_v_result:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nThis Tx is already used")
                return False
            if tp_v_result:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nThis Tx is already pooled")
                return False
            if bm_v_result2 is not True:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nThis Tx is unknown")
                return False
        return True

    def double_spending_in_block(self, transaction):
        v_result, used_outputs = self.rsa_util.verify_sbc_transaction_sig(transaction)
        if v_result is not True:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nsignature verification error on new transaction")
            return False

        for used_o in used_outputs:
            bm_v_result = self.bm.has_this_output_in_my_chain(used_o)
            bm_v_result2 = self.bm.is_valid_output_in_my_chain(used_o)
            if bm_v_result2 is not True:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nthis TransactionOutput is unknown")
                return False
            if bm_v_result:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nthis TransactionOutput is already used")
                return False
        return True

    def get_total_fee_on_block(self, block):
        #block checker
        #calculate the total fee on 'basic' Tx
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nget_total_fee_from_block was called")
        transactions = block["transactions"]
        result = 0
        for t in transactions:
            t = json.loads(t)
            checker, t_type = self.um.check_tx_type(t)
            if t_type == "basic":
                total_in = sum(i["transaction"][outputs][i["output_index"]]["value"] for i in t["inputs"])
                total_out = sum(o["value"] for o in t["outputs"])
                delta = total_in - total_out
                result += delta
        return result

    def check_transactions_in_new_block(self, block):
        #block checker
        #check whether Tx has a injustice
        fee_for_block = self.get_total_fee_on_block(block)
        fee_for_block += 30
        transactions = block["transactions"]
        counter = 0

        for t in transactions:
            t = json.loads(t)
            checker, t_type = self.um.is_sbc_transaction(t)
            if checker:
                if t_type == "basic":
                    if self.double_spending_in_block(t) is not True:
                        with open("/usr/local/server/log.txt", "a") as f:
                            f.write("\nBad Block. Having invalid Transaction")
                        return False
                elif t_type == "coinbase_transaction":
                    if counter != 0:
                        with open("/usr/local/server/log.txt", "a") as f:
                            f.write("\nCoinbaseTransaction is only for BlockBuilder")
                        return False
                    else:
                        insentive = t["outputs"][0]["value"]
                        with open("/usr/local/server/log.txt", "a") as f:
                            f.write("\ninsentive : {0}".format(insentive))
                        if insentive != fee_for_block:
                            with open("/usr/local/server/log.txt", "a") as f:
                                f.write("\nInvalid value in fee for CoinbaseTransaction")
                            return False
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nOK. this block is accepatable")
        return True


    def __handle_message(self, msg):
        # msg -> (result, sender, reason, cmd, payload)
        if msg[3] == MSG_NEW_TRANSACTION:
            new_transaction = json.loads(msg[4])
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nReceived new_transaction")
            checker, ans = self.um.check_tx_type(new_transaction)
            current_transactions = self.tp.get_stored_transactions()
            if new_transaction in current_transactions:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nthis is already pooled Tx")
                return
            else:
                if not checker:
                    with open("/usr/local/server/log.txt", "a") as f:
                        f.write("\nthis is not fikacoin Tx")
                else:
                    if self.bm.get_my_chain_length() != 1:
                        checked = self.double_spending(new_transaction)
                        if not checked:
                            with open("/usr/local/server/log.txt", "a") as f:
                                f.write("\nTransaction Verification Error")
                            return
                    self.tp.set_new_transaction(new_transaction)
                    new_message = self.cm.get_message_text(MSG_NEW_TRANSACTION, json.dumps(new_transaction))
                    if re.match("server", msg[1]):
                        self.cm.send_all(new_message, msg[1])
                    else:
                        self.cm.send_all(new_message)

        elif msg[3] == MSG_NEW_BLOCK:
            new_block = json.loads(msg[4])
            if self.bm.is_valid_block(self.previous_hash, new_block):
                if self.bb_running:
                    self.flag_stop_block_build = True
                self.previous_hash = self.bm.get_hash(new_block)
                self.bm.set_new_block(new_block)
                result = self.tp.get_stored_transactions()
                new_tp = self.bm.remove_used_tx(result)
                self.tp.renew_my_transactions(new_tp)

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
            new_message = self.cm.get_message_text(msg[3], msg[4])
            self.cm.send_all(new_message, msg[1])

    def __generate_block_with_tp(self):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\ngenerate_block_with_tp was called")

        while self.flag_stop_block_build is False:
            self.is_bb_running = True
            previous_hash = copy.copy(self.previous_hash)
            result = self.tp.get_stored_transactions()
            if len(result) == 0:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nTransactionPool is empty")
                break
            new_tp = self.bm.remove_used_tx(result)
            self.tp.renew_my_transactions(new_tp)
            if len(new_tp) == 0:
                break
            total_fee = self.tp.get_total_fee_from_tp()
            ###
            total_fee += 30
            ###
            my_coinbase_t = CoinbaseTransaction(self.km.my_address(), total_fee)
            transactions_4_block = copy.deepcopy(new_tp)
            transactions_4_block.insert(0, my_coinbase_t.to_dict())
            new_block = self.bb.generate_new_block(transactions_4_block, previous_hash)

            if new_block.to_dict()["previous_hash"] == self.previous_hash:
                self.bm.set_new_block(new_block.to_dict())
                self.previous_hash = self.bm.get_hash(new_block.to_dict())
                new_message = self.cm.get_message_text(MSG_NEW_BLOCK, json.dumps(new_block.to_dict()))
                self.cm.send_all(new_message)

                index = len(result)
                self.tp.clear_my_transactions(index)
                break
            else:
                with open("/usr/local/server/log.txt", "a") as f:
                    f.write("\nBad Block. It seems someone already win the PoW")
                break

        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nCurrent Blockchain is...\n{0}".format(self.bm.chain))
            f.write("\nCurrent previous_hash is...{0}".format(self.previous_hash))
        self.flag_stop_block_build = False
        self.is_bb_running = False
        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()


server = ServerCore()

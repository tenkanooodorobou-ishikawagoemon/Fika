# coding: utf-8

import os
import json
import threading
import pickle
import signal
import codecs
import time
import re
import socket
import subprocess
from socket_make import Socket
from message_manager import (
    MessageManager,
    MSG_NEW_TRANSACTION,
    MSG_NEW_BLOCK,
    MSG_REQUEST_FULL_CHAIN,
    RSP_FULL_CHAIN,
    MSG_REQUEST_LOG,
    RSP_LOG,
    ERR_PROTOCOL_UNMATCH,
    ERR_VERSION_UNMATCH,
    OK_WITH_PAYLOAD,
    OK_WITHOUT_PAYLOAD,
    MSG_TEST,
)

class ConnectionManager:
    def __init__(self, name, callback):
        self.name = name
        with open('/usr/local/server/neighbour_server_{0}.txt'.format(self.name), 'r') as f:
            texta = f.read()
        arg = "ls /usr/local/server".split()
        check_list = subprocess.check_output(arg).decode().split()
        if "neighbour_client_{0}.txt".format(self.name) in check_list:
            with open('/usr/local/server/neighbour_client_{0}.txt'.format(self.name), 'r') as f:
                textb = f.read()
            self.client_node = json.loads(textb)
            with open('/usr/local/server/log.txt', 'a') as f:
                f.write("\nClient node: {0}".format(self.client_node))

        with open('/usr/local/server/my_data_{0}.txt'.format(self.name), 'r') as f:
            textc = f.read()
        self.server_node = json.loads(texta)
        self.my_data = json.loads(textc)
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nServer node: {0}".format(self.server_node))
            f.write("\nMydata: {0}".format(self.my_data))
        self.mm = MessageManager()
        self.callback = callback

    def start(self):
        ip_num = self.my_data.values()
        for i in ip_num:
            socket = threading.Thread(target = Socket, args = (i[0], int(i[1]), self.__handle_message))
            socket.start()

    def get_message_text(self, msg_type, payload = None):
        msg = self.mm.build(self.name, msg_type, payload)
        return msg

    def send_all(self, msg, remove_node = None):
        if remove_node != None:
            for i in self.server_node:
                if i != remove_node:
                    self.send_msg(tuple(self.server_node[i]), msg)
        else:
            for i in self.server_node:
                self.send_msg(tuple(self.server_node[i]), msg)

    def send_msg(self, peer, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer))
            s.sendall(msg.encode())
            s.close()
        except OSError:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nSend msg failed")

    def __handle_message(self, params):
        soc, addr, data_sum = params
        while True:
            data = soc.recv(1024)
            data_sum = data_sum + data.decode()
            if not data:
                break
        if not data_sum:
            return

        result, sender, reason, cmd, payload = self.mm.parse(data_sum)
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\n{0}, {1}, {2}, {3}".format(result, sender, reason, cmd))
        status = (result, reason)

        if status == ("ERROR", ERR_PROTOCOL_UNMATCH):
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nError: Protocol name is not matched")
            return
        elif status == ("ERROR", ERR_VERSION_UNMATCH):
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nError: Protocol version is not matched")
            return
        elif status == ("OK", OK_WITHOUT_PAYLOAD):
            if re.match("server", sender):
                for i in self.server_node:
                    if i == sender:
                        peer = tuple(self.server_node[i])
            elif re.match("client", sender):
                for i in self.client_node:
                    if i == sender:
                        peer = tuple(self.client_node[i])
            self.callback((result, sender, reason, cmd, payload), peer)
        elif status == ("OK", OK_WITH_PAYLOAD):
            self.callback((result, sender, reason, cmd, payload))
        else:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nUnexpected status")

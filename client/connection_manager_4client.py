# coding: utf-8

import json
import socket
import threading
import pickle
import signal
import codecs
import time
import os
from socket_make import Socket
from message_manager import (
    MessageManager,
    MSG_NEW_TRANSACTION,
    MSG_REQUEST_FULL_CHAIN,
    RSP_FULL_CHAIN,
    MSG_REQUEST_LOG,
    RSP_LOG,
    ERR_PROTOCOL_UNMATCH,
    ERR_VERSION_UNMATCH,
    OK_WITH_PAYLOAD,
    OK_WITHOUT_PAYLOAD,
)

class ConnectionManager4Client:
    def __init__(self, name, callback):
        self.name = name
        with open('/usr/local/client/neighbour_server_{0}.txt'.format(self.name), 'r') as f:
            texta = f.read()
        with open('/usr/local/client/my_data_{0}.txt'.format(self.name), 'r') as f:
            textb = f.read()
        self.server_node = json.loads(texta)
        self.my_data = json.loads(textb)
        print("Server node: {0}".format(self.server_node))
        print("Mydata: {0}".format(self.my_data))
        self.mm = MessageManager()
        self.callback = callback

    def start(self):
        ip_num = self.my_data.values()
        for i in ip_num:
            socket = threading.Thread(target = Socket, args = (i[0], int(i[1]), self.__handle_message))
            socket.start()

    def get_message_text(self, msg_type, payload = None):
        msg = self.mm.build(self.name, msg_type, payload)
        peer = tuple(list(self.server_node.values())[0])
        return peer, msg

    def send_msg(self, peer, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer))
            s.sendall(msg.encode())
            s.close()
        except:
            print("Send msg failed")

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
        print(result, sender, reason, cmd)
        status = (result, reason)

        if status == ("ERROR", ERR_PROTOCOL_UNMATCH):
            print("Error: Protocol name is not matched")
            return
        elif status == ("ERROR", ERR_VERSION_UNMATCH):
            print("Error: Protocol version is not matched")
            return
        elif status == ("OK", OK_WITHOUT_PAYLOAD):
            if cmd == "RSP_LOG":
                print(payload)
        elif status == ("OK", OK_WITH_PAYLOAD):
            self.callback((result, sender, reason, cmd, payload))
        else:
            print("Unexpected status")

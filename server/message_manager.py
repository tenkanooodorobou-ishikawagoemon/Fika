# coding: utf-8

from distutils.version import StrictVersion
import json

PROTOCOL_NAME = "fika_coin"
VERSION = "0.1.0"

MSG_NEW_TRANSACTION = "NEW_TRANSACTION"
MSG_NEW_BLOCK = "NEW_BLOCK"
MSG_REQUEST_FULL_CHAIN = "REQUEST_FULL_CHAIN"
RSP_FULL_CHAIN = "RSP_FULL_CHAIN"
MSG_REQUEST_LOG = "REQUEST_LOG"
RSP_LOG = "RSP_LOG"
MSG_TEST = "TEST"

ERR_PROTOCOL_UNMATCH = 0
ERR_VERSION_UNMATCH = 1
OK_WITH_PAYLOAD = 2
OK_WITHOUT_PAYLOAD = 3

class MessageManager:
    def __init__(self):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nInitializing MessageManager...")

    def build(self, sender, msg_type, payload = None):
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nBuild a message")
        message = {
            "protocol": PROTOCOL_NAME,
            "version": VERSION,
            "sender": sender,
            "msg_type": msg_type,
        }
        show_message = json.dumps(message, indent = 4)
        if payload is not None:
            message["payload"] = payload
        return_message = json.dumps(message)
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\n{0}".format(show_message))
        return return_message

    def parse(self, msg):
        msg = json.loads(msg)
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nReceived a Message")
            f.write("\n{0}".format(json.dumps(msg, indent = 4)))
        msg_ver = StrictVersion(msg["version"])
        cmd = msg.get("msg_type")
        sender = msg.get("sender")
        payload = msg.get("payload")
        if msg["protocol"] != PROTOCOL_NAME:
            return ("ERROR", ERR_PROTOCOL_UNMATCH, None, None, None)
        elif msg_ver > StrictVersion(VERSION):
            return ("ERROR", ERR_VERSION_UNMATCH, None, None, None)
        elif cmd in (MSG_NEW_TRANSACTION, MSG_NEW_BLOCK, RSP_FULL_CHAIN, MSG_TEST):
            result_type = OK_WITH_PAYLOAD
            return("OK", sender, result_type, cmd, payload)
        else:
            result_type = OK_WITHOUT_PAYLOAD
            return ("OK", sender, result_type, cmd, None)

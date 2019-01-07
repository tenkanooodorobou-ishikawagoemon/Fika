# coding: utf-8

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii
import subprocess

class KeyManager:
    def __init__(self, name):
        print("Initializing KeyManager...")
        arg = "ls".split()
        check_list = subprocess.check_output(arg).decode().split()
        if "privatekey_{0}.pem".format(name) not in check_list:
            random_gen = Crypto.Random.new().read
            self.privatekey = RSA.generate(2048, random_gen)
            self.publickey = self.privatekey.publickey()
            private_pem = self.privatekey.exportKey()
            with open("/usr/local/client/privatekey_{0}.pem".format(name), "w") as f:
                f.write(private_pem.decode())
            self.signer = PKCS1_v1_5.new(self.privatekey)
        else:
            f = open("/usr/local/client/privatekey_{0}.pem".format(name), "r")
            self.privatekey = RSA.importKey(f.read())
            f.close()
            self.publickey = self.privatekey.publickey()
            self.signer = PKCS1_v1_5.new(self.privatekey)

    def my_address(self):
        return binascii.hexlify(self.publickey.exportKey(format = "DER")).decode("ascii")

    def compute_digital_signature(self, message):
        hashed_message = SHA256.new(message.encode())
        signer = PKCS1_v1_5.new(self.privatekey)
        return binascii.hexlify(signer.sign(hashed_message)).decode("ascii")

    def verify_signature(self, message, signature, sender_public_key):
        hashed_message = SHA256.new(message.encode())
        verifier = PKCS1_v1_5.new(sender_public_key)
        return verifier.verify(hashed_message, binascii.unhexlify(signature))

    def import_key_pair(self, key_data):
        self.privatekey = RSA.importKey(key_data)
        self.publickey = self.privatekey.publickey()
        self.signer = PKCS1_v1_5.new(self.privatekey)

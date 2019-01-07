import re
import json
import binascii
import subprocess
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA

from shcommand import *

class Equipment:
    def __init__(self, jailname):
        self.name = jailname
        self.neighbour_server = dict()
        self.neighbour_client = dict()
        self.my_data = dict()
        arg = "jls host.hostname".split()
        check_list = subprocess.check_output(arg).decode("utf-8").split()
        if jailname not in check_list:
            jailc(jailname)
            mt_devfs(jailname)
            mt_nullfs(jailname)
            jexec(jailname, "ifconfig lo0 127.0.0.1/24 up")
            jexec(jailname, "ipfw add allow ip from any to any")

    def create_key(self):
        random_gen = Crypto.Random.new().read
        self.privatekey = RSA.generate(2048, random_gen)
        self.publickey = self.privatekey.publickey()
        private_pem = self.privatekey.exportKey()
        with open("privatekey_{0}.pem".format(self.name), "w") as f:
            f.write(private_pem.decode())
        arg = "mv privatekey_{0}.pem /jails/{0}/usr/local/client".format(self.name).split()
        subprocess.run(arg)
        return binascii.hexlify(self.publickey.exportKey(format = "DER")).decode("ascii")

    def regist_neighbour(self, obj):
        obj_name = obj[0]
        obj_ip = obj[1]
        obj_port = int(obj[2])
        if re.match("server", obj_name):
            self.neighbour_server[obj_name] = [obj_ip, obj_port]
            print("{0} connect with {1}".format(self.name, self.neighbour_server))
        elif re.match("client", obj_name):
            self.neighbour_client[obj_name] = [obj_ip, obj_port]
            print("{0} connect with {1}".format(self.name, self.neighbour_client))
        else:
            print("Unknown name...")

    def regist_mydata(self, epair, ip, port):
        data = [ip, port]
        self.my_data[epair] = data

    def json_out(self):
        connected_node = json.dumps(self.neighbour_server)
        my_data = json.dumps(self.my_data)
        with open("neighbour_server_{0}.txt".format(self.name), "w") as f:
            f.write(connected_node)
        with open("my_data_{0}.txt".format(self.name), "w") as f:
            f.write(my_data)
        if len(self.neighbour_client) != 0:
            connected_client = json.dumps(self.neighbour_client)
            with open("neighbour_client_{0}.txt".format(self.name), "w") as f:
                f.write(connected_client)

    def destroy(self):
        print("destroy {0}".format(self.name))
        jname = self.name
        #
        arg = "jexec {0} ifconfig -l".format(jname).split()
        ifnames = subprocess.check_output(arg).decode("utf-8").split()
        #
        epairs = [i for i in ifnames if re.match("epair.*", i)]
        for epair in epairs:
            ifconfig("{0} -vnet {1}".format(epair, jname))
            ifconfig("{0} destroy".format(epair))
        bridges = [j for j in ifnames if re.match("vbridge.*", j)]
        for bridge in bridges:
            ifconfig("{0} -vnet {1}".format(bridge, jname))
            ifconfig("{0} destroy".format(bridge))
        print("do umount_nullfs {0}".format(jname))
        umt_nullfs(jname)
        print("done umount_nullfs {0}".format(jname))
        arg = "jail -r {0}".format(jname).split()
        subprocess.run(arg)
        print("do umount_devfs {0}".format(jname))
        umt_devfs(jname)
        print("done umount_devfs {0}".format(jname))

    def connect(self, epair):
        name = self.name
        ifconfig("{0} vnet {1}".format(epair, name))

    def disconnect(self, epair):
        name = self.name
        ifconfig("{0} -vnet {1}".format(epair, name))

    def assignip(self, epair, ip, mask):
        name = self.name
        jexec(name, "ifconfig {0} inet {1} netmask {2}".format(epair, ip, mask))

    def up(self, epair):
        name = self.name
        jexec(name, "ifconfig {0} up".format(epair))

    def down(self, epair):
        name = self.name
        jexec(name, "ifconfig {0} down".format(epair))

    def start(self, program):
        name = self.name
        jexec(name, "/usr/local/etc/rc.d/{0} start".format(program))

# coding: utf-8

import json
import subprocess
import re
from shcommand import *
from equipment import Equipment

class Operator:
    def __init__(self):
        self.daicho = dict()
        self.servers = []
        self.clients = []
        self.client_pubkey = dict()
        num = 0
        self.epair_num = num
        print("I'll do your job")

    def createpair(self):
        num = 0
        arg = "ifconfig epair create".split()
        output = subprocess.check_output(arg).decode("utf-8").split()
        output = [i for i in output if re.match("epair\d+a", i)][0]
        num = output.replace("epair", "").replace("a", "")
        ifconfig("epair{0}a link 02:c0:e4:00:{0}:0a".format(num))
        ifconfig("epair{0}b link 02:c0:e4:00:{0}:0b".format(num))
        self.num = num
        return "epair{0}a".format(num), "epair{0}b".format(num)

    def destroypair(epair):
        if re.match("epair\d+[ab]", epair) != False:
            epair = epair[:-1]
        ifconfig("{0}a destroy".format(epair))
        del self.daicho["{0}a".format(epair)]
        del self.daicho["{0}b".format(epair)]

    def register(self, epair, jailname, ip4 = None, mask = None, AS = None, ip6 = None, prefixlen = None):
        self.daicho[epair] = [jailname, ip4, mask, AS, ip6, prefixlen]

    def unregister(self, epair):
        del self.daicho[epair]

    def find(self, epair):
        return self.daicho[epair]

    def setupserver(self, jailname):
        exec("{0} = Equipment('{0}')".format(jailname),  globals())
        print("Setup server {0} done!".format(jailname))
        self.servers.append("{0}".format(jailname))

    def setupclient(self, jailname):
        exec("{0} = Equipment('{0}')".format(jailname), globals())
        pubkey = eval("{0}.create_key()".format(jailname))
        print("Setup client {0} done!".format(jailname))
        self.clients.append("{0}".format(jailname))
        self.client_pubkey[jailname] = pubkey

    def connect(self, obj, epair):
        exec("{0}.connect('{1}')".format(obj, epair))
        #
        self.daicho[epair] = [obj, "", ""]
        #
        print("{0} is connected to {1}".format(epair, obj))

    def assignip(self, obj, epair, ip, mask, port, AS = None):
        exec("{0}.assignip('{1}', '{2}', '{3}')".format(obj, epair, ip, mask))
        #ip6 = self.find(epair)[4]
        #prefixlen = self.find(epair)[5]
        #self.daicho[epair] = [obj, ip, mask, AS, ip6, prefixlen]
        self.daicho[epair] = [obj, ip, mask, AS]
        print("{0} of {1} has {2}/{3}".format(epair, obj, ip, mask))
        exec("{0}.regist_mydata('{1}','{2}','{3}')".format(obj, epair, ip, port))

    def up(self, obj, epair):
        exec("{0}.up('{1}')".format(obj, epair))
        print("{0} up".format(epair))

    def down(self, obj, epair):
        exec("{0}.down('{1}')".format(obj, epair))
        print("{0} down".format(epair))

    def record(self, obj1, obj2):
        param = obj2.split()
        exec("{0}.regist_neighbour({1})".format(obj1, param))

    def startserver(self):
        for s in self.servers:
            exec("{0}.json_out()".format(s))
            arg = "mv neighbour_server_{0}.txt /jails/{0}/usr/local/server".format(s).split()
            subprocess.run(arg)
            arg2 = "mv my_data_{0}.txt /jails/{0}/usr/local/server".format(s).split()
            subprocess.run(arg2)
            check = subprocess.check_output("ls").decode().split()
            if "neighbour_client_{0}.txt".format(s) in check:
                arg3 = "mv neighbour_client_{0}.txt /jails/{0}/usr/local/server".format(s).split()
                subprocess.run(arg3)
            arg4 = "jexec {0} python3.6 /usr/local/server/server_core.py".format(s).split()
            subprocess.Popen(arg4)
            print("{0} start!!".format(s))

    def startclient(self):
        key_list = json.dumps(self.client_pubkey)
        with open("key_list.txt", "w") as f:
            f.write(key_list)
        for c in self.clients:
            exec("{0}.json_out()".format(c))
            arg = "mv neighbour_server_{0}.txt /jails/{0}/usr/local/client".format(c).split()
            subprocess.run(arg)
            arg2 = "mv my_data_{0}.txt /jails/{0}/usr/local/client".format(c).split()
            subprocess.run(arg2)
            arg3 = "cp key_list.txt /jails/{0}/usr/local/client".format(c).split()
            subprocess.run(arg3)
            print("{0} start!!".format(c))

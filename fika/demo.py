#!/usr/local/bin/python3.6
from fika import Operator

global jails
jails = '/jails'
shuma = Operator()
shuma.setupserver("server1")
shuma.setupserver("server2")
shuma.setupserver("server3")
shuma.setupclient("client1")
shuma.setupclient("client2")

# Port number
# server -> 50000~
# client -> 60000~
# serverX -> X00
# epairYa or epairYb -> Y
#
# if server3 && connect with epair8a, the interface's port number is
# => 50308

epair0a, epair0b = shuma.createpair()
shuma.connect("server1", epair0a)
shuma.connect("server2", epair0b)
shuma.assignip("server1", epair0a, "192.168.0.1", "255.255.255.0", 50100)
shuma.assignip("server2", epair0b, "192.168.0.2", "255.255.255.0", 50200)
shuma.up("server1", epair0a)
shuma.up("server2", epair0b)
#shuma.record("Recorder", "Neighbour Neighbour'sIPaddress Neighbour'sPort")
shuma.record("server1", "server2 192.168.0.2 50200")
shuma.record("server2", "server1 192.168.0.1 50100")

epair1a, epair1b = shuma.createpair()
shuma.connect("server1", epair1a)
shuma.connect("server3", epair1b)
shuma.assignip("server1", epair1a, "192.168.1.1", "255.255.255.0", 50101)
shuma.assignip("server3", epair1b, "192.168.1.2", "255.255.255.0", 50301)
shuma.up("server1", epair1a)
shuma.up("server3", epair1b)
shuma.record("server1", "server3 192.168.1.2 50301")
shuma.record("server3", "server1 192.168.1.1 50101")


epair2a, epair2b = shuma.createpair()
shuma.connect("server1", epair2a)
shuma.connect("client1", epair2b)
shuma.assignip("server1", epair2a, "192.168.2.1", "255.255.255.0", 50102)
shuma.assignip("client1", epair2b, "192.168.2.2", "255.255.255.0", 60102)
shuma.up("server1", epair2a)
shuma.up("client1", epair2b)
shuma.record("server1", "client1 192.168.2.2 60102")
shuma.record("client1", "server1 192.168.2.1 50102")


epair3a, epair3b = shuma.createpair()
shuma.connect("server3", epair3a)
shuma.connect("client2", epair3b)
shuma.assignip("server3", epair3a, "192.168.3.1", "255.255.255.0", 50303)
shuma.assignip("client2", epair3b, "192.168.3.2", "255.255.255.0", 60203)
shuma.up("server3", epair3a)
shuma.up("client2", epair3b)
shuma.record("server3", "client2 192.168.2.2 60203")
shuma.record("client2", "server3 192.168.2.1 50303")

shuma.startserver()
shuma.startclient()

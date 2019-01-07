import socket

class Socket:
    def __init__(self, ip, port, callback):
        self.my_ip = ip
        self.my_port = port
        self.callback = callback
        with open("/usr/local/server/log.txt", "a") as f:
            f.write("\nip : {0}, port : {1}".format(self.my_ip, self.my_port))
        self.socket_make(self.my_ip, self.my_port)

    def socket_make(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))
        self.socket.listen(0)

        while True:
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nWaiting for the connection...")
            soc, addr = self.socket.accept()
            with open("/usr/local/server/log.txt", "a") as f:
                f.write("\nConnected by...{0}".format(addr))
            data_sum = ''
            params = (soc, addr, data_sum)
            self.callback(params)

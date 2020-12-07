# Import semua module yang dibutuhkan
from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *
from pyretic.modules.mac_learner import mac_learner
from datetime import datetime
# Penerapan Load-Balancing Round-Robin
# Paket pertama akan di drop -> identifikasi
# Merubah Alur dari
# client -> public address(virtual), dimana client -> server
# server -> client, dimana public address(virtual) -> client
def rubah_alur(cli, ser, pub):
    cli_pub = match(srcip=cli, dstip=pub)
    ser_cli = match(srcip=ser, dstip=cli)
    
    return ((cli_pub >> modify(dstip=ser)) + (ser_cli >> modify(srcip=pub)) + (~cli_pub & ~ser_cli))

class rrlb(DynamicPolicy):
# Inisialisasi
    def __init__(self, clients, servers, public_ip): super(rrlb,self).__init__()
        self.clients = clients
        self.servers = servers
        self.public_ip = public_ip
        self.index = 0
        
        self.query = packets(limit=1,group_by=['srcip']) #
    traffic monitoring
        self.query.register_callback(self.update_policy) #
    Callback Query
        self.lb_policy = None
        self.policy = (match(dstip=self.public_ip) +
    match(dstport=80) >> self.query)

    def update_policy(self, pkt):
        client = pkt['srcip']
 # Agar server tidak di redirect ke dirinya sendiri
        if client in self.servers:
            return
 # Memanggil fungsi Round-Robin
        server = self.round_robin()
 # Memanggil fungsi load-balancing
        p = rubah_alur(client, server, self.public_ip)
        print"Memetakan Client:%s ke Server:%s" % (client,server)
        if self.lb_policy:
            self.lb_policy = self.lb_policy >> p
        else:
            self.lb_policy = p


        self.policy = self.policy + self.lb_policy
 # Pemilihan server dengan metode Round_Robin
    def round_robin(self):
        server = self.servers[self.index % len(self.servers)]
        self.index += 1
        return server

    def hitung_paket():
        q = count_packets(2.5,['srcip','dstip'])
        q.register_callback(hitung_paket_print)
        return q

    def hitung_paket_print(counts):
        print "----Perhitungan Banyak Paket----"
        print datetime.now().time().isoformat()
        if counts:
            for pred, pkt_byte_count in counts.iteritems():
                print pred, ':', pkt_byte_count
        else:
            print 'Belum Ada Paket Data yang Mengalir.'
    def hitung_pakets():
        pass
    def hitung_paket_prints(counts):
        pass
    def main(clients=15, servers=3):
        clients = int(clients)
        servers = int(servers)
        ip_prefix = "10.0.0."
        ip_public = IP(ip_prefix + "100")



 # Menentukan IP address untuk clients
        ip_client = []
        for i in range(1, clients+1):
            alamat_ip = IP(ip_prefix+str(i))
            ip_client.append(alamat_ip)

 # Menentukan IP address untuk servers
        ip_server = []
        for i in range(1+clients, clients+servers+1):
            alamat_ip = IP(ip_prefix+str(i))
            ip_server.append(alamat_ip)

        print"Alamat IP Publik adalah %s" % ip_public
        print "Alamat Server: "
        for i in range(0, servers):
            print "Server ",int(i+1), " : ", ip_server[i]
            print ""

        print "Alamat Client: "
        for i in range(0, clients):
            print "Client ", int(i+1), " : ", ip_client[i]
            print ""
        return (rrlb(ip_client, ip_server, ip_public) + hitung_paket()) >> mac_learner()
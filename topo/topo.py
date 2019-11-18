#coding=utf-8

import networkx as nx
import matplotlib.pyplot as plt
from mininet.topo import Topo
from mininet.log import setLogLevel,info
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.util import dumpNodeConnections

# 从gml文件读入数据，构建拓扑
file = './data.gml'

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        G = nx.read_gml('./data.gml')
        name_to_return = dict()
        name_to_switch = dict()
        index = 1
        for node in G.nodes():
            name_to_switch[node] = 's%d' % index
            name_to_return[node] = self.addSwitch('s%d' % index)
            temp_host = self.addHost('h%d' % index, ip='10.0.0.%d' % index, mac='00:00:00:00:00:%02x' % index)
            self.addLink(temp_host, name_to_return[node])
            index += 1

        for u, v in G.edges():
            self.addLink(name_to_return[u], name_to_return[v])
        nx.draw(G, with_labels=True, font_weight='bold')
        plt.savefig("graph.png", format="PNG")

topos = {'mytopo': (lambda : MyTopo())}
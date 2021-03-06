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
f = 'dataset/data13.gml'

# 逐行解析GML文件
def parse_gml(filename):
    try:
        with open(filename) as f:
            lines = f.read().splitlines()
        sz = len(lines)
        ind = 0
        node_list, edge_list = list(), list()
        while ind < sz:
            if lines[ind].lstrip() == "node [":
                ind += 1
                temp = lines[ind].lstrip().split()
                if temp[1].isdigit():
                    node_list.append(int(temp[1]) + 1)
                while ind < sz and lines[ind].lstrip() != "]":
                    ind += 1
            elif lines[ind].lstrip() == "edge [":
                ind += 1
                src = lines[ind].lstrip().split()
                if src[0] == 'source' and src[1].isdigit():
                    ind += 1
                    dst = lines[ind].lstrip().split()
                    if dst[0] == 'target' and dst[1].isdigit():
                        edge_list.append((int(src[1]) + 1, int(dst[1]) + 1))
                while ind < sz and lines[ind].lstrip() != "]":
                    ind += 1
            ind += 1
        return node_list, edge_list
    except IOError:
        print "file not found!"

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        
        node_list, edge_list = parse_gml(f)
        G = nx.Graph()

        for u, v in edge_list:
            G.add_edge('s%d' % u, 's%d' % v)
        switches, hosts = dict(), dict()
        for id in node_list:
            G.add_edge('h%d' % id, 's%d' % id)    
            switches['s%d' % id] = self.addSwitch('s%d' % id)
            hosts['h%d' % id] = self.addHost('h%d' % id, ip='10.0.0.%d' % id, mac='00:00:00:00:00:%02x' % id)
            self.addLink(switches['s%d' % id], hosts['h%d' % id])
        
        for u, v in edge_list:
            self.addLink(switches['s%d' % u], switches['s%d' % v])
        
        nx.draw(G, with_labels=True, font_weight='bold')
        plt.savefig("graphs/graph13.png", format="PNG")

topos = {'mytopo': (lambda : MyTopo())}
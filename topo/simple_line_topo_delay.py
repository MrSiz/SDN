#coding=utf-8

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.util import dumpNodeConnections

#带延迟

def simple_topo():
    net = Mininet(link=TCLink)
    # 添加控制器
    net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6653)
    s1 = net.addSwitch('s1')
    # s2 = net.addSwitch('s2')
    # s3 = net.addSwitch('s3')
    # 设置主机的IP地址
    h1, h2 = net.addHost('h1', ip='10.0.0.1'), net.addHost('h2', ip='10.0.0.2')
    # self.addLink(host, switch, bw=10, delay='5ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(s1, h1, delay='0ms')
    # net.addLink(s1, s2, delay='0ms')
    # net.addLink(s2, s3, delay='0ms')
    net.addLink(s1, h2, delay='0ms')
    net.start()
    CLI(net)

if __name__ == '__main__':
    simple_topo()
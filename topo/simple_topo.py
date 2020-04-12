#coding=utf-8

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI

def simple_topo():
    net = Mininet()
    # 添加控制器
    net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6653)
    s1 = net.addSwitch('s1')
    # 设置主机的IP地址
    h1, h2 = net.addHost('h1', ip='10.0.0.1'), net.addHost('h2', ip='10.0.0.2')
    net.addLink(s1, h1, port1=1, port2=1)
    net.addLink(s1, h2, port1=2, port2=1)
    net.start()
    CLI(net)

if __name__ == '__main__':
    simple_topo()
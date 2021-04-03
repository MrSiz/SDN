# coding=utf-8

# 基于IP层的TOS字段进行转发

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import packet, ethernet, ether_types, arp, icmp, ipv4
from ryu.ofproto import ofproto_v1_3, ofproto_v1_4
from ryu.topology import event
from collections import defaultdict
import networkx as nx
from ryu.topology.api import get_link, get_all_link


class Forward(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    DELAYPORT = 20
    CNT = 0
    def __init__(self, *args, **kwargs):
        super(Forward, self).__init__(*args, **kwargs)
        self.init_flag = False
        self.topology_api_app = self
        self.network = nx.DiGraph()
        self.mac_to_port = {}
        self.dpid_to_datapath = {}
        self.topology_api_app = self
        self.arp_port = {}
        self.flag = defaultdict(bool)
        self.ip_route = defaultdict(bool)
        self.ip_port = {}
        self.ip_flag = defaultdict(bool)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.dpid_to_datapath[datapath.id] = datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, 0, match, actions, hard_timeout=0, idle_timeout=0)


    def add_flow(self, datapath, priority, match, actions,hard_timeout=0,idle_timeout = 0, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    hard_timeout=hard_timeout,
                                    idle_timeout=idle_timeout,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    hard_timeout=hard_timeout,
                                    idle_timeout=idle_timeout,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(event.EventSwitchEnter)
    def process_switch_enter(self, ev):
        print "--switch enter--"

        link_list = get_all_link(self.topology_api_app)

        links = list()
        for link in link_list:
            links.append((link.src.dpid, link.dst.dpid, {'port': link.src.port_no, link.src.dpid: link.src.port_no, link.dst.dpid:link.dst.port_no}))
            links.append((link.dst.dpid, link.src.dpid,
                          {'port': link.dst.port_no, link.src.dpid: link.src.port_no, link.dst.dpid: link.dst.port_no}))
            print "links %s %s: " % (link.src.dpid, link.dst.dpid) , link.src.port_no
            self.network.add_node(link.src.dpid, connected=dict())
            self.network.add_node(link.dst.dpid, connected=dict())
            # print self.network.nodes
            self.network.node[link.src.dpid]['connected'][link.src.port_no] = link.dst.dpid
            self.network.node[link.dst.dpid]['connected'][link.dst.port_no] = link.src.dpid


        print "links: ", links
        self.network.add_edges_from(links)

    def add_host(self, host_mac, inport, dpid):
        if host_mac not in self.network:
            print "add host into network:", host_mac
            self.network.add_node(host_mac, connected=dict())
            self.network.node[host_mac]['connected'][inport] = dpid

            self.network.add_edge(host_mac, dpid, port=inport)
            self.network.add_edge(dpid, host_mac, port=inport)


    def get_path(self, src, dst):
        if dst in self.network:
            return nx.shortest_path(self.network,src, dst)
        return []

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        print "packet-in"
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        print "eth.ethertype = %x" % eth.ethertype
        if eth.ethertype == ether_types.ETH_TYPE_IPV6:
            return
        elif eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        elif eth.ethertype == ether_types.ETH_TYPE_ARP:
            print "arp"
            arp_pkt = pkt.get_protocol(arp.arp)
            self.add_host(arp_pkt.src_mac, in_port, datapath.id)

            dpid = datapath.id
            dst_mac = eth.dst
            src_mac = eth.src

            temp = (dpid, src_mac, arp_pkt.dst_ip)
            # 记录入端口,避免网络风暴
            if not self.flag[temp]:
                self.flag[temp] = True
                self.arp_port[temp] = in_port
            elif self.flag[temp] and self.arp_port[temp] != in_port:
                print "rep", self.CNT
                print "in_port: ", in_port, "table_port: ",
                self.CNT += 1
                return

            self.mac_to_port.setdefault(dpid, {})
            self.mac_to_port[dpid][src_mac] = in_port
            if dst_mac in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst_mac]
            else:
                out_port = ofproto.OFPP_FLOOD
            # out_port = ofproto.OFPP_FLOOD
            # print "out_port: ", out_port
            actions = [ofp_parser.OFPActionOutput(out_port)]
            print temp, out_port
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = ofp_parser.OFPPacketOut(
                datapath=datapath, buffer_id = msg.buffer_id, in_port=in_port, actions=actions, data=data
            )
            datapath.send_msg(out)

        elif eth.ethertype == ether_types.ETH_TYPE_IP:
            ippart = pkt.get_protocol(ipv4.ipv4)
            print "======"
            dst_mac = eth.dst
            src_mac = eth.src
            print "src_ip: ", ippart.src
            print "dst_ip: ", ippart.dst
            dpid = datapath.id
            path = self.get_path(dpid, dst_mac)

            if path:
                print "path: ", path

                for i in xrange(len(path) - 1):
                    temp_dpid = path[i]
                    temp_outport = self.network[path[i]][path[i + 1]]['port']
                    match = ofp_parser.OFPMatch(eth_type=0x0800,ip_dscp=ippart.tos,
                                                ipv4_src=ippart.src, ipv4_dst=ippart.dst)
                    actions = [ofp_parser.OFPActionOutput(temp_outport)]
                    self.add_flow(self.dpid_to_datapath[temp_dpid], priority=10, match=match, actions=actions, hard_timeout=10)
                data = None
                if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                    data = msg.data
                actions = [ofp_parser.OFPActionOutput(self.network[path[0]][path[1]]['port'])]
                out = ofp_parser.OFPPacketOut(
                    datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data
                )
                datapath.send_msg(out)
            else:
                print "null path"
                return
        else:
            pass
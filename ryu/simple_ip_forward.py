# coding=utf-8

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import ether_types
from ryu.lib.packet import arp
from collections import  defaultdict


# 功能
# 控制器根据arp报文，记录mac地址和转发端口，在收到新的ip报文时再下发对应规则，进行转发

class SIMPE_IP_FORWARD(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SIMPE_IP_FORWARD, self).__init__(*args, **kwargs)
        self.flag = defaultdict(bool)

        # 记录数据包是从交换机的哪个端口收到的
        self.arp_port = {}

        # 记录mac地址对应的端口号
        self.mac_to_port = {}

    # 控制器与交换机建立连接时，下发默认规则到交换机上，默认将不匹配的流上传到控制器处理
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    # 控制器处理收到的PacketIn消息
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packetin_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)

        # 获得以太网帧头部
        eth = pkt.get_protocol(ethernet.ethernet)
        self.logger.info("PacketIn switch: %s, port: %s, from:%s to %s", datapath.id, in_port, eth.src, eth.dst)
        # 过滤掉ipv6，lldp数据包
        if eth.ethertype == ether_types.ETH_TYPE_IPV6:
            return
        elif eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        elif eth.ethertype == ether_types.ETH_TYPE_ARP:
            arp_pkt = pkt.get_protocol(arp.arp)
            dpid = datapath.id
            src_mac = arp_pkt.src_mac
            dst_mac = arp_pkt.dst_mac
            # self.add_host(src_mac, in_port, dpid)
            temp = (dpid, src_mac, arp_pkt.dst_ip)

            if not self.flag[temp]:
                self.flag[temp] = True
                self.arp_port[temp] = in_port
            elif self.flag[temp] and self.arp_port[temp] != in_port:
                # 记录了的消息来自于同一交换机的不同端口，则不处理，以此避免网络风暴
                return

            self.mac_to_port.setdefault(dpid, {})
            self.mac_to_port[dpid][src_mac] = in_port

            # 如果目的mac已经存在mac表中，则从mac表中获得出端口，
            # 否则广播出去
            if dst_mac in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst_mac]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [ofp_parser.OFPActionOutput(out_port)]
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = ofp_parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
        elif eth.ethertype == ether_types.ETH_TYPE_IP:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            dst_mac = eth.dst
            dpid = datapath.id

            if dst_mac in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst_mac]
            else:
                out_port = None
            if not out_port:
                self.logger("ERROR: No matched outport")
                return
            else:
                # 找到了对应的出端口，再做两件事
                # 1. 下发流规则到交换机
                # 2. 将数据包转发出去
                match = ofp_parser.OFPMatch(eth_type=0x800, in_port=in_port, ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst)
                actions = [ofp_parser.OFPActionOutput(out_port)]
                self.add_flow(datapath, 10, match, actions)

                data = None
                if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                    data = msg.data
                out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                          in_port=in_port, actions=actions, data=data)
                datapath.send_msg(out)
        else:
            pass
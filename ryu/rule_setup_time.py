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

# 安装一条默认转发的流规则到交换机上

class DEFAULT(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DEFAULT, self).__init__(*args, **kwargs)

    # 控制器与交换机建立连接时，下发默认规则到交换机上
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

    # 安装规则到交换机
    # 拓扑为h1-s1-h2
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packetin_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath 
        ofproto = datapath.ofproto 
        ofp_parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)

        eth = pkt.get_protocol(ethernet.ethernet)

        # 实验中只发udp进行测试
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            out_port = 2 # 构造拓扑的时候设定
            # 先下发flowmod消息
            match = ofp_parser.OFPMatch(eth_type=0x800, in_port=in_port, ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst)
            actions = [ofp_parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 10, match, actions)            
            # 再下发packetout消息
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data 
            out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                          in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
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
        in_port = 1
        out_port = 2
        ip_src = '10.0.0.1'
        ip_dst = '10.0.0.2'
        match = parser.OFPMatch(eth_type=0x800, in_port=in_port, ipv4_src=ip_src, ipv4_dst=ip_dst)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(datapath, 100, match, actions)
    
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
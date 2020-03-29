#coding=utf-8

"""
提供给Cbench测试用
"""

from ryu.ofproto import ofproto_v1_0
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER

class Forward(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def send_flow_mod(self, datapath, port):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        match = ofp_parser.OFPMatch(in_port = port)
        cookie = 0
        command = ofp.OFPFC_ADD
        idle_timeout = hard_timeout = 0
        priority = 32768
        buffer_id = 0xffffffff
        out_port = 10
        flags = 0
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 0)]
        req = ofp_parser.OFPFlowMod(
            datapath, match, cookie, command, idle_timeout, hard_timeout,
            priority, buffer_id, out_port, flags, actions)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packetin_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        inport = msg.in_port
        self.send_flow_mod(dp, inport)
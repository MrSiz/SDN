#coding=utf-8

"""
提供给Cbench测试用
"""

from ryu.ofproto import ofproto_v1_0
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER

from collections import defaultdict
from Queue import Queue

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

    # 功能模拟函数
    def work(self):
        graph = {
        # 交换机的id
        0: [4, 5, 10],
        1: [4, 5, 11],
        2: [6, 7, 12],
        3: [6, 7, 13],
        4: [0, 8, 9],
        5: [1, 8, 9],
        6: [2, 8, 9],
        7: [3, 8, 9],
        8: [4, 5, 6, 7],
        9: [4, 5, 6, 7],

        # 主机的id
        10: [0],
        11: [1],
        12: [2],
        13: [3]
        }
        s = 11 # 源主机
        t = 13 # 目的主机

        # print(s, t)
        que = Queue()
        que.put(s)
        dis = [1000000] * 100
        dis[s] = 0
        vis = [False] * 100
        pre = defaultdict(int)
        vis[s] = True
        pre[s] = -1
        while not que.empty():
            u = que.get()
            if u == t:
                break
            vis[s] = False
            # print(graph[u])
            for v in graph[u]:
                if dis[v] > dis[u] + 1:
                    dis[v] = dis[u] + 1
                    pre[v] = u
                    if not vis[v]:
                        que.put(v)
                        vis[v] = True
        if pre[t] == -1:
            return None
        path = [t]
        while pre[t] != -1:
            path.append(pre[t])
            t = pre[t]
        path[0] -= 10
        path[-1] -= 10
        path.reverse()

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packetin_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        inport = msg.in_port
        # self.work()
        self.send_flow_mod(dp, inport)
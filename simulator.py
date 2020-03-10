#coding=utf-8

from queue import Queue
from threading import Thread
from collections import defaultdict

import signal
import os
import random
import time 
import math 
import copy 

#   拓扑结构

#    s8          s9
#  |/  |/    \|      \|
#  s4   s5   s6     s7
#  |/   \|   |/     \|
#  s0   s1   s2     s3
#  |    |    |      |
#  h0   h1   h2     h3


host_nums = 4
switch_nums = 12

controller_queue = Queue()
host_queues = [Queue()] * host_nums
switch_queues = [Queue()] * switch_nums


"""
数据包通过字典传递
1. 代表源到目的的普通数据包
"""

# 封装数据包
def gen_packet(msg_type, content, time_tick):
    return {
        "type": msg_type,
        "content": content,
        "time": time_tick
    }


# 主机产生数据包，往相邻交换机里面放
def host_work(host_id, switch_id):
    print('host_id %d' % (host_id))
    lamb = 0.5
    need_add = False
    packet_gen_time = -1
    while True:
        if not need_add:
            packet_gen_time = now() + exp(lamb)
            need_add = True
        if need_add == True and now() > packet_gen_time:
            dst_host_id = host_id
            while dst_host_id == host_id:
                dst_host_id = random.randint(0, 3)
            switch_queues[switch_id].put(gen_packet(1, (host_id, dst_host_id), now()))
            need_add = False
            print('host_id:{0} dst_host_id: {1}\n'.format(host_id, dst_host_id))
            # break


# 交换机处理数据包
def switch_work(switch_id):
    # 记录从源到目的的出现次数
    print("switch_id %d" % (switch_id))
    vis = {}
    is_proc = False 
    mu = 0.7
    packet_proc_time = -1
    nxt_switch = {}
    while True:
        if not is_proc:
            is_proc = True
            packet_proc_time = now() + exp(mu)

        if is_proc == True and now() > packet_proc_time:
            data = switch_queues[switch_id].get()
            message_type = data["type"]
            print('nxt_switch{2} switch id{0}: {1}\n'.format(switch_id, data, nxt_switch))
            if message_type == 1:
                src = data["content"][0]
                dst = data["content"][1] 
                vis.setdefault(src, {})
                nxt_switch.setdefault(src, {})
                print('initialize nxt_switch{0}'.format(nxt_switch))
                if dst in vis[src]:
                    vis[src][dst] += 1
                    # 传到相邻的交换机去
                    nxt_hop = nxt_switch[src][dst]
                    if nxt_hop != -1:
                        switch_queues[nxt_hop].put(gen_packet(1, (src, dst), now()))
                else:
                    vis[src][dst] = 1
                    nxt_switch[src][dst] = -1
                    controller_queue.put(gen_packet(2, (src, dst), now()))
            elif message_type == 3:
                path = data["content"]
                for i in range(1, len(path)):
                    if path[i] == switch_id:
                        print('path i: {0}\n'.format(path[i]))
                        print('src: {0} dst:{1} nxt_switch:{2}\n'.format(path[0], path[-1], nxt_switch))
                        if i + 1 < len(path) and path[i + 1] != path[-1]:
                            print('{0} --- {1}'.format(path[0], path[1]))
                            nxt_switch[path[0]][path[-1]] = path[i + 1]
                        else:
                            nxt_switch[path[0]][path[-1]] = -1

            
            is_proc = False
        

# 控制器收到第一次上传上来的数据包的时候
# 计算可行路径
def get_path(graph, s, t):
    s += 10
    t += 10
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
    return copy.deepcopy(path)

# 控制器接收处理数据包
def controller_work():
    graph = {
        # 交换机的id
        0 : [4, 5, 10],
        1 : [4, 5, 11],
        2 : [6, 7, 12],
        3 : [6, 7, 13],
        4 : [0, 8, 9],
        5 : [1, 8, 9],
        6 : [2, 8, 9],
        7 : [3, 8, 9],
        8 : [6, 7],
        9 : [6, 7],

        # 主机的id
        10 : [0],
        11 : [1],
        12 : [2],
        13 : [3]
    }
    print("????")
    mu = 0.7
    is_proc = False
    packet_proc_time = -1
    dict_path = {}
    while True:
        # print('.')
        if not is_proc:
            is_proc = True
            packet_proc_time = now() + exp(mu)
        if is_proc and now() > packet_proc_time:
            data = controller_queue.get()
            print("controller: {0}\n".format(data))
            if data["type"] == 2:
                src = data["content"][0]
                dst = data["content"][1]
                dict_path.setdefault(src, {})
                path = None
                if dst in dict_path[src]:
                    path = dict_path[src][dst]
                else:
                    path = get_path(graph, src, dst)
                    dict_path[src][dst] = path
                print('path{0}'.format(path))
                print('get path from {0} to {1}: {2}\n'.format(src, dst, path))

                if path is not None:
                    for switch in path[1:-1]:
                        print('controller to swith {0}\n'.format(switch))
                        switch_queues[switch].put(gen_packet(3, copy.deepcopy(path), now()))
            is_proc = False

def now():
    """
    返回当前的时间，单位是毫秒级
    """
    return int(round(time.time() * 1000))

def exp(lambd):
    """
    返回指数分布的值
    """    
    # 方法1:
    # return random.expovariate(lambd)
    # 方法 2:
    return -math.log(1 - random.random()) / lambd

def signal_handler(signum, frame):
    print('进程被终止\n')
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    controller_thread = Thread(target=controller_work, args=(), daemon=True)
    controller_thread.start()
    # controller_thread.join()

    swtich_thread = []
    for i in range(switch_nums):
        swtich_thread.append(Thread(target=switch_work, args=(i,), daemon=True))
    for s in swtich_thread:
        s.start()

    host_thread = []
    for i in range(host_nums):
        host_thread.append(Thread(target=host_work, args=(i,i,), daemon=True))
    for h in host_thread:
        h.start()
    
    while True:
        # controller_queue.put(gen_packet(2, (0, 1), now()))
        # time.sleep(3)
        pass

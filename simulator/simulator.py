# coding=utf-8


"""
TODO:
中间交换机收到数据包的时间需要改变
删除时间戳，按照收到的时间计算

只有pending的数据包才会有时间戳

"""

from queue import Queue
from threading import Thread
from collections import defaultdict
from threading import Lock
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
switch_nums = 10

controller_queue = Queue()
host_queues = [Queue() for i in range(host_nums)]
switch_queues = [Queue() for i in range(switch_nums)]

# 模拟的时长，单位: 秒
MAXTIME = 30


# swith_queueu_lock = Lock()
# 封装数据包
def gen_packet(msg_type, content, time_tick=0.0, swith_id=-1):
    return {
        "type": msg_type,
        "content": content,
        "time": time_tick,
        "switch_id": swith_id #控制器可以看到
    }


def signal_handler(signum, frame):
    print('进程被终止\n')
    exit(0)


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


def now():
    """
    返回当前的时间，单位是秒级
    """
    return time.time()


def exp(lambd):
    """
    返回指数分布的值
    """
    # 方法1:
    # return random.expovariate(lambd)
    # 方法 2:
    return -math.log(1 - random.random()) / lambd


# 主机产生数据包，往相邻交换机里面放
def host_work(host_id, switch_id):
    lamb = 0.7
    STOP_TIME = now() + MAXTIME
    cnt = defaultdict(int)
    vis = defaultdict(int)
    while now() <= STOP_TIME:
        # if host_id != 0: # 调试用，需注释
        #     break 
        dst_host_id = host_id
        while dst_host_id == host_id:
            # 随机得到目的主机的id
            dst_host_id = random.randint(0, 3)
        if vis[(host_id, dst_host_id)] == 0:
            vis[(host_id, dst_host_id)] = 1
            # print('({0} {1})\n'.format(host_id, dst_host_id))
        # print('host[{0}] ({1} {2} addinto switch[{3}])\n'.format(host_id, host_id, dst_host_id, switch_id))
        # 按照指数时间间隔向相邻交换机发送数据包
        time.sleep(exp(lamb))
        # with swith_queueu_lock:
        # print('host:[{0}] ({1}, {2})\n'.format(host_id, host_id, dst_host_id))
        switch_queues[switch_id].put(gen_packet(1, (host_id, dst_host_id), now()))
        cnt[dst_host_id] += 1
        # break
    print(' host_id:{0} cnt:{1}\n'.format(host_id, cnt))


# 交换机处理数据包
def switch_work(switch_id):
    # 记录从源到目的的出现次数
    # nxt = defaultdict(lambda : -2)
    mu = 1.0
    # -2表示未确定下一跳
    # -1 表示下一跳为主机
    # 正数表示交换机
    nxt_switch = defaultdict(lambda: -2)
    STOP_TIME = now() + MAXTIME
    wait_time = 0.0
    consumer_num = 0
    pending = Queue()
    ispend = defaultdict(int)
    # nor_cnt, pend_cnt = 0, 0
    while now() <= STOP_TIME:
        # print('switch_id{0}\n'.format(switch_id))
        # 服务时间服从指数分布
        # print('time now:{0}\n'.format(now()))
        try:
            # with swith_queueu_lock:
            data = switch_queues[switch_id].get(block=False)
        except:
            continue
        wait_time += now() - data["time"]
        consumer_num += 1
        serv_time = exp(mu)
        # 普通的数据包
        if data["type"] == 1:
            src = data["content"][0]
            dst = data["content"][1]
            time.sleep(serv_time)
            # 不知道该数据包的下一跳 且是第一次收到该数据包，就上传到控制器和缓冲队列中
            if nxt_switch[(src, dst)] == -2 and ispend[(src, dst)] == 0:
                ispend[(src, dst)] = 1
                
                # print('switch:[{0}] ({1}, {2}) up \n'.format(switch_id, src, dst))
                controller_queue.put(gen_packet(2, (src, dst), now(), switch_id))
                pending.put(copy.deepcopy(data))
            # 不是第一次收到该数据包，但还不知道怎么转发，就放到缓冲队列中
            elif nxt_switch[(src, dst)] == -2 and ispend[(src, dst)] == 1:
                pending.put(copy.deepcopy(data))
            # 收到数据包，并且知道它的下一跳，就把该数据包发到下一跳交换机
            elif nxt_switch[(src, dst)] != -1 and nxt_switch[(src, dst)] != -2:
                # with swith_queueu_lock:
                switch_queues[nxt_switch[(src, dst)]].put(gen_packet(1, (src, dst), now()))

                # 在把数据包转发给其他交换机的时候统计时间
                # wait_time += serv_time
                # consumer_num += 1
                
                # print('switch:[{0}] ({1}, {2}) forward {3}\n'.format(switch_id, src, dst, nxt_switch[(src, dst)]))
            # 值为-1，则表示下一跳是主机，不传过去了
            elif nxt_switch[(src, dst)] == -1:
                pass
                # 收到控制器下发的消息
        elif data["type"] == 3:
            # print('receveid from controller, switch_id:{0}\n'.format(switch_id))
            # 控制器下发给交换机的消息中包含路径
            path = data["content"]
            # print('received from controller')
            # 相当于交换机在处理flowmod消息
            # wait_time += serv_time
            time.sleep(serv_time)
            # consumer_num += 1
            for i in range(1, len(path)):
                if path[i] == switch_id:
                    # print('path{0} index{1}\n'.format(path, i))
                    if i + 1 < len(path):
                        # print('path[{0} {1}]\n'.format(path[0], path[-1]))
                        nxt_switch[(path[0], path[-1])] = path[i + 1]
                    else:
                        nxt_switch[(path[0], path[-1])] = -1
                    break 
            # 把缓冲的数据包都转发出去
            temp = Queue()
            # print('switch {1} sizeof pending:{0}\n'.format(pending.qsize(), switch_id))
            while pending.qsize() != 0:
                try:
                    data = pending.get(block=False)
                except:
                    break
                src = data["content"][0]
                dst = data["content"][1]
                # print('will forward to {0}\n'.format(nxt_switch[(src, dst)]))
                # 给pending的数据包再加一个处理延时
                pending_serv_time = 0 
                if nxt_switch[(src, dst)] != -2:
                    # pend_cnt += 1
                    if nxt_switch[(src, dst)] == -1:
                        # 现在的时间 - 加入缓冲队列的时间
                        pending_serv_time = exp(mu)
                        time.sleep(pending_serv_time)
                        wait_time += now() - data["time"]
                        consumer_num += 1
                        # print('switch:[{0}] ({1}, {2}) pending forward \n'.format(switch_id, src, dst))
                    else:
                        # with swith_queueu_lock:
                        pending_serv_time = exp(mu)
                        time.sleep(pending_serv_time)
                        switch_queues[nxt_switch[(src, dst)]].put(gen_packet(1, (src, dst), now()))
                        wait_time += now() - data["time"]
                        # print('switch:[{0}] ({1}, {2}) pending forward \n'.format(switch_id, src, dst))
                        consumer_num += 1
                else:
                    # 继续缓冲着
                    # print('???????')
                    temp.put(data)
            pending = temp
        # print('swith_id{2} wait_time: {0} cnt:{1}\n'.format(wait_time, consumer_num, switch_id))
    print('switch_id:{0} total_wait_time:{1} total_consumer:{2}\n'.format(switch_id, wait_time, consumer_num))


# 控制器接收处理数据包
def controller_work():
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
    mu = 1.0
    dict_path = {}
    STOP_TIME = now() + MAXTIME
    wait_time = 0.0
    consumer_num = 0
    while now() <= STOP_TIME:
        try:
            data = controller_queue.get(block=False)
        except:
            # print('no data\n')
            continue
        # print('controller\n')

        serv_time = exp(mu)
        now_time = now()
        dif = now_time - data['time']
        wait_time += dif   
        time.sleep(serv_time) 
        # print('now:{1} pre:{2}controller_wait_time:{0} diff:{3} serv:{4}'.format(wait_time, now_time, data['time'], dif, serv_time))
        consumer_num += 1
        src = data["content"][0]
        dst = data["content"][1]
        print('controller switch_id:[{0}] ({1}, {2})\n'.format(data["switch_id"], src, dst))
        dict_path.setdefault(src, {})
        # print('(( controller [{2}] {0}  {1}) serv_time: {3})'.format(src, dst, data["switch_id"], serv_time))
        path = None
        if dst in dict_path[src]:
            path = dict_path[src][dst]
        else:
            path = get_path(graph, src, dst)
            dict_path[src][dst] = path

        if path is not None:
            for switch in path[1:-1]:
                # print('controller to swith {0}\n'.format(switch))        
                # with swith_queueu_lock:
                switch_queues[switch].put(gen_packet(3, copy.deepcopy(path), now()))
    print('controller total_wait_time:{0} total_consumer:{1} \n'.format(wait_time, consumer_num))


if __name__ == '__main__':
    random.seed(int(time.time()))
    signal.signal(signal.SIGINT, signal_handler)

    controller_thread = Thread(target=controller_work, args=(), daemon=False)
    controller_thread.start()
    # controller_thread.join()

    swtich_thread = []
    for i in range(switch_nums):
        swtich_thread.append(Thread(target=switch_work, args=(i,), daemon=False))
    for s in swtich_thread:
        s.start()

    host_thread = []
    for i in range(host_nums):
        host_thread.append(Thread(target=host_work, args=(i, i,), daemon=False))
    for h in host_thread:
        h.start()

    for s in swtich_thread:
        s.join()

    for h in host_thread:
        h.join()

    # while True:
    #     # controller_queue.put(gen_packet(2, (0, 3), now()))
    #     pass
    


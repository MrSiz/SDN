#### 测试环境
+ ubuntu 18.04
+ 8核CPU、8G内存

----
### 测试控制器服务率


### 测试一
在控制器一端模拟数据包处理的功能

#### 1个交换机
测试指令`./cbench -c 127.0.0.1 -p 6633 -s 1 -l 4 -t`,结果如下:
```
10:09:18.718 1   switches: flows/sec:  8993   total = 8.989611 per ms 
10:09:19.818 1   switches: flows/sec:  8986   total = 8.984850 per ms 
10:09:20.920 1   switches: flows/sec:  9046   total = 9.037351 per ms 
10:09:22.021 1   switches: flows/sec:  9009   total = 8.999856 per ms 
RESULT: 1 switches 3 tests min/max/avg/stdev = 8984.85/9037.35/9007.35/22.08 responses/s
```

#### 2个交换机
测试指令`./cbench -c 127.0.0.1 -p 6633 -s 2 -l 4 -t`,结果如下:
```
10:11:05.106 2   switches: flows/sec:  4403  4274   total = 8.649840 per ms 
10:11:06.207 2   switches: flows/sec:  4387  4386   total = 8.767862 per ms 
10:11:07.309 2   switches: flows/sec:  4339  4338   total = 8.659663 per ms 
10:11:08.413 2   switches: flows/sec:  4355  4354   total = 8.676463 per ms 
RESULT: 2 switches 3 tests min/max/avg/stdev = 8659.66/8767.86/8701.33/47.54 responses/s
```

----
### 测试二
在控制器一端不模拟数据包处理的功能

#### 1个交换机
测试指令`./cbench -c 127.0.0.1 -p 6633 -s 1 -l 4 -t`,结果如下:
```
10:14:46.728 1   switches: flows/sec:  15105   total = 15.094494 per ms 
10:14:47.830 1   switches: flows/sec:  15139   total = 15.126642 per ms 
10:14:48.932 1   switches: flows/sec:  13953   total = 13.943825 per ms 
10:14:50.033 1   switches: flows/sec:  15473   total = 15.464309 per ms 
RESULT: 1 switches 3 tests min/max/avg/stdev = 13943.82/15464.31/14844.93/651.92 responses/s
```

#### 2个交换机
测试指令`./cbench -c 127.0.0.1 -p 6633 -s 2 -l 4 -t`,结果如下:
```
10:15:50.434 2   switches: flows/sec:  7327  7183   total = 14.509927 per ms 
10:15:51.534 2   switches: flows/sec:  7299  7284   total = 14.582942 per ms 
10:15:52.635 2   switches: flows/sec:  7253  7252   total = 14.499490 per ms 
10:15:53.736 2   switches: flows/sec:  7124  7109   total = 14.232431 per ms 
RESULT: 2 switches 3 tests min/max/avg/stdev = 14232.43/14582.94/14438.29/149.50 responses/s
```

---
## 测试交换机
总共发送了2w个数据包。

### 测试存在流规则的情况
拓扑结构是`h1-s1-h2`,测试结果如下:
```
# 第一次
(0.33560599999882135, 70000) # 所有包总的时间 总数
4.79437142855e-06 # 平均时间
208577.915771  # 1s / 平均时间 = 1s 能处理的数据包个数

# 第2次
(0.10950900000041891, 20000)
5.47545000002e-06
182633.390862
```



### 测试处理新数据包产生PacketIn的情况
拓扑结构是`hs-s1-c`,测试结果如下:
```
(1.7136148630000179, 20000)
8.568074315e-05
11671.2339697
```
注:在真实情况下还有交换机和控制器互相发发`request/reply`消息


#### 异常
+ 当每次发包的源ip不同的时候(即每次发不同源ip的包，每次发1个)，服务率明显低于每次发相同的源ip相同的包(即只发源ip相同的包，交换机不安装流规则，发多个);
+ 前者的时间间隔短很容易导致tcpdump抓不到包，但是后者即便发包间隔很短，tcpdump仍能抓到。（怀疑是某种缓存机制?)
+ packetin消息产生的数量会出现与发包数量不一致的情况
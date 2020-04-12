#### 说明
介绍所用到的相关工具

----
### oflops
该工具支持对controller和switch进行性能测试。
+ 下载地址`https://github.com/mininet/oflops`

#### 安装
在oflops的仓库下有相关的说明，需要注意的是：
1. 依赖[openflow](!https://github.com/mininet/openflow)，所以要先安装上openflow。若已经安装了ovs，则在安装oflops的时候，直接`./configure`

----
### cbench
cbench可以用来测试控制器的性能，主要原理是伪造PacketIn消息发送给控制器，缺点是只支持OpenFlow1.0。cbench在oflops的子目录中，编译成功oflops就可以使用cbench了.

例子:
```
./cbench -c 127.0.0.1 -p 6633 -s 1 -l 4 -t
```
即：测试地址为`127.0.0.1:6633`的控制器，模拟一个交换机(`-s 1`)，循环4次(`-l 4`), `throughput`模式(`-t`)

两种模式:
1. Latency模式：Cbench发送一个packet in消息并等待控制器返回匹配的flow mod消息，如此反复多次，统计每秒内发生的次数即每秒内收到的flow mod数量。
2. Throughput模式：对于每个OpenFlow会话，在缓存满之前Cbench一直发送packet in消息，计算返回的flow mod数，统计每秒内控制器能够处理事务的数量。

#### 参考资料
+ https://www.sdnlab.com/15112.html

---
#### tcpdump
抓包工具，可以使用tcpdump直接从mininet的交换机上的网卡抓包。
```
sudo tcpdump udp -i s1-eth2 -Q out >> out.txt
```
使用上述命令即是只抓取`udp`报文，方向为`out`，重定向输出到`out.txt`文件，以便后续相关的分析。更多的使用方法可以参考`man tcpdump`。


#### tshark
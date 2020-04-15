#### 说明
论文实验记录, `quick`对应着发包间隔不高于1s,`slow`对应着发包间隔不低于1s。

#### 文件夹说明
+ `default_rule`：测试交换机存在默认流规则时候的服务率
+ `flow_rule`: 测试交换机安装流规则的服务率
+ `packetin`: 测试交换机产生PacketIn消息的服务率
+ `hops`: 测试在不同交换机跳数的情况下，延迟的大小

#### 方法说明
1. 默认流规则:预先在交换机上安装流规则，然后利用`packet/`下的发包代码进行发包，同时利用`tcpdump`在交换机的入口和出口抓包。
2. 安装流规则:控制器收到PacketIn消息后，根据ip地址进行流规则的安装，发包方法同`1`,利用`tcpdump`抓`loopback`的`openflow`报文，在交换机的出口抓`udp`报文。
3. 产生PacketIn消息:发包方法同`1`,控制器不处理`PacketIn`消息, `tcpdump`抓交换机的入口以及`loopback`的`openflow`报文。
4. 测试不同跳数：端到端的数据发送，采集入口交换机和出口交换机网卡上的数据包，通过差值计算出时间延迟，以及直接从接收端的数据包由时间戳计算得到时间延迟，两者进行比较。

#### 抓包命令
利用`tcpdump`在交换机的网卡上抓取某个方向的报文。
```shell
sudo tcpdump udp -i s1-eth2 -Q out > out.txt
```
利用`tshark`抓取`openflow`报文
```shell
sudo tshark -i lo -d tcp.port=6633,openflow -u s -t ad -o column.format:"Time","%Cus:frame.time","Source, %s","Destination, %d","Protocol, %p","Info, %i"  > in.txt
```
注:在抓包时，应根据不同的需求进行参数调整，重定向输出到文本，以便对数据进行处理。

#### 数据处理
主要利用`linux`下的管道及`awk`命令。
1. 处理`tcpdump`抓到的`udp`报文
```shell
cat in.txt | awk '{print $1}' | awk -F ':' '{print $3}' > in1.txt
```
2. 处理`tshark`抓取到的`openflow`报文
```shell
cat out.txt | awk '/OFPT_PACKET_IN$/' | awk '{print $4}' | awk -F ':' '{print $3}' > out1.txt

cat in.txt | awk '/OFPT_FLOW_MOD$/' | awk '{print $4}' | awk -F ':' '{print $3}' > in1.txt 
```
3. 利用各个文件夹下的`data_process.py`脚本没，对数据进行简单的计算

#### 其他
每个文件夹下的`1,2,3..`文件，表示的是第几次实验结果的记录。
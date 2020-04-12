#### 说明
按照不同的功能，对此文件夹下的文件进行说明。

#### 运行
在终端窗口中输入`ryu-manager xx.py --observe-links`      

**注**: `ryu`支持多个应用同时运行，所以可以加上多个`xx.py`文件，加上`--observe-links`会产生`LLDP`报文，以此实现控制器对交换机的发现。更多的命令行参数详见`ryu-manger --help`。

----

#### 基于IP地址的逐跳规则下发
该功能实现于`simple_ip_forward.py`文件。
+ 控制器根据收到的ARP消息，将mac地址和端口进行记录
+ 控制器再次收到带ip的消息后，根据原先的mac地址和端口记录，下发基于ip的流规则到交换机，然后再转发

这种方式导致了多次的PacketIn消息上传到控制器，所以前1,2个数据包的延迟会较高。

#### 针对控制器的性能测试
该测试主要实现于`flowmod_cbench.py`文件，需搭配Cbench使用。先运行该文件，再设置Cbench的相关参数，即可在Cbench一端得到相应的测试结果。

#### 针对交换机PacketIn产生速率的测试
该测试的控制器代码实现于`packetin_test.py`文件，该文件只在最开始下发一条默认的产生`PacketIn`消息的流规则,在正常收到`PacketIn`消息的时候，不做其他处理。

#### 针对交换机处理FlowMod消息的速率测试
该测试的控制器代码实现于`flowmod_cbench.py`文件，该文件在每次收到`PacketIn`消息的时候下发`Flowmod`消息到交换机上。
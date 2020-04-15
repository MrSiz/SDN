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

---
### 针对实验的控制器代码
以下的三个文件主要针对的是三个不同的实验，对应的拓扑代码为`topo/simple_topo.py`。

#### 针对交换机PacketIn产生速率的测试
该测试的控制器代码实现于`packetin_test.py`文件，控制器只在最开始下发一条默认的产生`PacketIn`消息的流规则,在正常收到`PacketIn`消息的时候，不做其他处理。

#### 针对交换机处理FlowMod消息的速率测试
该测试的控制器代码实现于`flowmod_cbench.py`文件，控制器在每次收到`PacketIn`消息的时候下发`Flowmod`消息到交换机上。

#### 针对交换机直接转发数据包速率的测试
该测试的控制器代码实现于`ryu_default_flowrule`文件，控制器在最开始下发一条默认的转发流规则。

#### 其他
+ 基于restapi的流规则下发, 格式如下，应使用`post`方法,url为`http://localhost:8080/stats/flowentry/modify`,body格式如下：

```
{
	"dpid": 1,
	"cookie": 1,
	"cookie_mask":1,
	"table_id":0,
	"idle_timeout":0,
	"hard_timeout":0,
	"priority":1111,
	"flags":1,
	"match":{
        "nw_src": "10.0.0.3",
        "in_port": 1,
        "nw_dst": "10.0.0.2"
	},
	"actions":[
		{
			“type”:”OUTPUT”, 
			“port”: 3 
		}
	]
}
```
[参考](https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html#add-a-flow-entry)
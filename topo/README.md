#### 说明
利用`networkx`从`data.gml`文件中读取数据,构建网络拓扑。其他网络拓扑可从`topology-zoo(http://www.topology-zoo.org/)`获取。文末介绍利用`mininet`的命令，直接创建简单的拓扑。

提供两种运行方法。

#### 依赖
+ `networkx`库

#### 方法一
运行`topo.py`。启动远程控制器后,终端下按顺序执行

```shell
sudo mn --clean
sudo mn --custom ./topo.py --topo mytopo --controller remote
```
#### 方法二
运行`main_topo.py`。

`sudo python main_topo.py`

**注意**: 拓扑可能存在环，所以需要在控制器一端处理环形拓扑，否则会出现网络风暴。

#### 更新
+ 预设主机`IP`和`MAC`地址。 2019.11.17
+ 保存拓扑图片和自定义`GML`解析函数。 2019.11.18
+ 增加`dataset`文件夹存储`GML`文件, 增加`graphs`文件夹存储拓扑图。 2019.11.19


---
### 其他
通过`man mn`可以看到mininet支持建立`linear|minimal|reversed|single|torus|tree`等结构的拓扑。在实验中，为了快速建立拓扑，可以使用mininet的`--topo`选项达到该目的。

+ 建立只有1个交换机的拓扑，即`single`,命令为`sudo mn --topo=single,4 --controller=remote`,数字`4`表示的是主机个数,`--controller=remote`表示连接到远程交换机，后文不再赘述。
+ 直线型，即`linear`。交换机连接为一条直线，命令为`sudo mn --topo=linear 4`,数字`4`表示的是主机和交换机个数皆为4,即1:1的关系。
+ 默认的,即`minimal`,只有1个交换机和2个主机连接着，命令为`sudo mn --topo=minimal`。

其余选项，读者可以自行尝试。

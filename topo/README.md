#### 说明
利用`networkx`从`data.gml`文件中读取数据,构建网络拓扑。其他网络拓扑可从`topology-zoo(http://www.topology-zoo.org/)`获取。

#### 依赖
+ `networkx`库

#### 运行
启动远程控制器后,终端下按顺序执行
```shell
sudo mn --clean
sudo mn --custom ./topo.py --topo mytopo --controller remote
```
**注意**: 拓扑可能存在环，所以需要在控制器一端处理环形拓扑，否则会出现网络风暴。
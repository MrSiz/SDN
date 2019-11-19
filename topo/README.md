#### 说明
利用`networkx`从`data.gml`文件中读取数据,构建网络拓扑。其他网络拓扑可从`topology-zoo(http://www.topology-zoo.org/)`获取。

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
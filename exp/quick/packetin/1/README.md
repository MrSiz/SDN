#### 处理in.txt文件
`cat in.txt | awk '{print $1}' | awk -F ':' '{print $3}' > in1.txt`

#### 处理out.txt文件
`cat out.txt | awk '/OFPT_PACKET_IN$/' | awk '{print $4}' | awk -F ':' '{print $3}' > out1.txt
`


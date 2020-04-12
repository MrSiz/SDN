#coding=utf-8

# 处理tcpdump收集的数据

def process(ret, filename):
    with open(filename) as in_file:
        lines = in_file.readlines()
        print(len(lines))
        for line in lines:
            if len(line) > 5:
                temp = line.split()[0]
                second = temp.split(':')
                ret.append(float(second[2]))
    return 

if __name__ == '__main__':
    # 默认的分割符号
    sep = ' '
    # 处理的文件名
    filename1 = '2/in.txt'
    input_times = []
    process(input_times, filename1)

    filenmae2 = '2/out.txt'
    output_times = []
    process(output_times, filenmae2)

    sum = 0.0
    for i in range(len(input_times)):
        if output_times[i] >= input_times[i]:
            sum += output_times[i] - input_times[i]
    print(sum, len(input_times))
    avg = sum / len(input_times)
    print(avg)
    serve_rate = 1 / avg
    print(serve_rate)

# (0.33560599999882135, 70000)
# 4.79437142855e-06
# 208577.915771

#coding=utf-8

# 处理收集的数据

def process(ret, filename):
    cnt = 0
    with open(filename) as in_file:
        lines = in_file.readlines()
        for line in lines:
            if len(line) > 5:
                cnt += 1
                # print(float(line))
                ret.append(float(line))
    print(cnt)
    return 

if __name__ == '__main__':
    # 默认的分割符号
    sep = ' '
    # 处理的文件名
    filename1 = '4/in1.txt'
    input_times = []
    process(input_times, filename1)

    filenmae2 = '4/out1.txt'
    output_times = []
    process(output_times, filenmae2)

    sum = 0.0
    cnt = 0
    for i in range(len(input_times)):
        if output_times[i] >= input_times[i]:
            sum += output_times[i] - input_times[i]
            cnt += 1
    print(sum, cnt)
    avg = sum / cnt
    print(avg)
    serve_rate = 1 / avg
    print(serve_rate)

# (0.33560599999882135, 70000)
# 4.79437142855e-06
# 208577.915771
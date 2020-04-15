#coding=utf-8

# 处理收集的数据

def process(ret, filename):
    with open(filename) as in_file:
        lines = in_file.readlines()
        for line in lines:
            if len(line) > 5:
                ret.append(float(line))
    return 

import numpy as np

def remove_outliers(arr):
    res = []

    Q1 = np.percentile(arr, 25)

    Q3 = np.percentile(arr, 75)

    IQR = Q3 - Q1 
    step = 1.5 * IQR

    for ele in arr:
        if ele < Q1 - step or ele > Q3 + step:
            arr.remove(ele)
    return arr 


if __name__ == '__main__':
    # 默认的分割符号
    sep = ' '
    # 处理的文件名
    filename1 = '3/in1.txt'
    input_times = []
    process(input_times, filename1)

    filenmae2 = '3/out1.txt'
    output_times = []
    process(output_times, filenmae2)

    arr = []
    pre_ans = 0
    pre_cnt = 0
    i, j = 0, 0
    while i < len(input_times):
        if output_times[j] >= input_times[i]:
            temp = output_times[j] - input_times[i]
            if temp > 10:
                j += 1
                continue 
                # print(i, output_times[j], input_times[i])
            pre_ans += output_times[j] - input_times[i]
            arr.append(temp)
            pre_cnt += 1
            # print('%.6f' % temp)
        else:
            temp = output_times[j] + 60 - input_times[i]
            # print('%.6f' % temp)
            if temp > 10:
                j += 1
                continue 
                # print(i, output_times[j], input_times[i])
            pre_ans += output_times[j] + 60 - input_times[i]
            arr.append(temp)
            pre_cnt += 1
        i += 1
        j += 1
    arr.sort()
    arr = remove_outliers(arr)
    ans = sum(arr)
    cnt = len(arr)
    print('---------pre---------')
    print(pre_ans, pre_cnt)
    pre_avg = pre_ans / pre_cnt
    print(pre_avg)
    pre_serve_rate = 1 / pre_avg 
    print (pre_serve_rate)
    print('---------now---------')
    print(ans, cnt)
    avg = ans / cnt
    print(avg)
    serve_rate = 1 / avg
    print(serve_rate)

# (0.33560599999882135, 70000)
# 4.79437142855e-06
# 208577.915771

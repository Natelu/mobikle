import pandas as pd
import numpy as np
import os
import math
import time
from pandas import Series,DataFrame
#数据
PATH=r'data'
FILE=r'train_group.csv'
UNCLASSIFIED = False
NOISE = 0
# df=DataFrame.from_csv(PATH+os.sep+FILE,header=None,sep=',',encoding='utf-8')
# dr=pd.read_csv(PATH+os.sep+FILE)
# dr.sort_values(by=['userid','starttime'],ascending=[1,1],inplace=True)
# dr.to_csv(r'data\train_group.csv')

#两点之间欧氏距离,参数-点（x,y）
def dist(a,b):
    lat1=float(a[0])
    lon1=float(a[1])
    lat2=float(b[0])
    lon2=float(b[1])
    dx = np.abs(lon1 - lon2)  # 经度差
    dy = np.abs(lat1 - lat2)  # 维度差
    b = (lat1 + lat2) / 2.0
    Lx = 6371004.0 * (dx / 57.2958) * np.cos(b / 57.2958)
    Ly = 6371004.0 * (dy / 57.2958)
    L = (Lx**2 + Ly**2) ** 0.5
    # print('{}和{}距离是{}'.format(a,b,L))
    return L

# 两点ab是否在eps范围内
def eps_neighbor(a, b, eps):
    return dist(a, b) < eps

# 输入：数据集, 查询点id, 半径大小
# 输出：在eps范围内的点的id
def region_query(data, pointId, eps):
    nPoints = data.shape[0]
    seeds = []
    for i in range(nPoints):
        if eps_neighbor(data[pointId,: ], data[i,: ], eps):
            seeds.append(i)
    return seeds

# 输入：数据集, 分类结果, 待分类点id, 簇id, 半径大小, 最小点个数
# 输出：能否成功分类
def expand_cluster(data, clusterResult, pointId, clusterId, eps, minPts):
    seeds = region_query(data, pointId, eps)
    if len(seeds) < minPts: # 不满足minPts条件的为噪声点
        clusterResult[pointId] = NOISE
        return False
    else:
        clusterResult[pointId] = clusterId # 划分到该簇
        for seedId in seeds:
            clusterResult[seedId] = clusterId

        while len(seeds) > 0: # 持续扩张
            currentPoint = seeds[0]
            queryResults = region_query(data, currentPoint, eps)
            if len(queryResults) >= minPts:
                for i in range(len(queryResults)):
                    resultPoint = queryResults[i]
                    if clusterResult[resultPoint] == UNCLASSIFIED:
                        seeds.append(resultPoint)
                        clusterResult[resultPoint] = clusterId
                    elif clusterResult[resultPoint] == NOISE:
                        clusterResult[resultPoint] = clusterId
            seeds = seeds[1:]
        return True

#   输入：数据集, 半径大小, 最小点个数
#   输出：分类簇id
def dbscan(data, eps, minPts):
    clusterId = 1
    nPoints = data.shape[0]
    clusterResult = [UNCLASSIFIED] * nPoints
    print(clusterResult)
    for pointId in range(nPoints):
        point = data[pointId,: ]
        if clusterResult[pointId] == UNCLASSIFIED:
            if expand_cluster(data, clusterResult, pointId, clusterId, eps, minPts):
                clusterId = clusterId + 1
    return clusterResult, clusterId - 1,data.tolist()

if __name__ == "__main__":
    t0 = time.clock()
    input=open(PATH+os.sep+FILE,'r')
    output=open(PATH+os.sep+'cluster.txt','w+')
    all_lines=input.readlines()
    list_user=[]    #临时存贮每一个用户的坐标序列
    i=0
    cur_user=1
    for line in all_lines:
        #首行 & 筛选有价值列
        items = line.split(',')
        if i==0:
            print('开始处理第一行')
        else:
            try:
                if cur_user!=items[1]:
                    data = np.array(list_user)
                    res = dbscan(data, 100, 4)
                    output.write(str(cur_user)+','+str(res)+'\n')
                    cur_user = items[1]
                    list_user = []
                tuple_1 = (items[4].replace('\n', '')).split(' ')
                tuple_2 = (items[4].replace('\n', '')).split(' ')
                list_user.append(tuple_1)
                list_user.append(tuple_2)
            except:
                print('第%i行数据有误' % i)
        i=i+1
        print('已处理{}行'.format(i))
    res = dbscan(np.array(list_user), 100, 4)  #处理最后一个用户
    output.write(str(cur_user) + ',' + str(res) + '\n')
    input.close()
    output.close()
    print('用时{}秒'.format(time.clock() - t0))
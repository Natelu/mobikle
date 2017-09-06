import os
import sys
import Geohash
target_dir=r'D:\lu_work\python\data'
from_file='train.csv'
to_file='train_lat.csv'
input=open(target_dir+os.sep+from_file,'r')
output=open(target_dir+os.sep+to_file,'w+')
log=open(target_dir+os.sep+'log.txt','w+')
all_train_lines=input.readlines()
i=0
#逐行转换起始点坐标
for line in all_train_lines:
    #首行 & 筛选有价值列
    items = line.split(',')
    if i==0:
        output.write(items[0]+items[1]+','+items[4]+','+items[5]+','+items[6]+'\n')
    else:
        try:
            st_pri = items[6].replace('\n', '')
            en_pri = items[5].replace('\n', '')
            start = Geohash.decode(st_pri)
            end = Geohash.decode(en_pri)
            output.write(items[0]+items[1] + ',' + items[4] + ',' + start[0] + ' ' + start[1] + ',' + end[0] + ' ' + end[1] + '\n')
        except:
            log.write(items[0]+'订单号转换坐标有错误\n')
    i=i+1
    print(i)
output.close()
log.close()
#coding:utf-8

import random


## 二分搜索 ##
def bin_search(arr,data,low,high):

    if low > high:
        return "not found "

    middle = (low + high) / 2

    if data < arr[middle]:
        return bin_search(arr,data,low,middle-1)
    elif data > arr[middle]:
        return bin_search(arr,data,middle+1,high)
    else:
        return "found %d, index is %d" %(data,middle)

if __name__ == '__main__':

    a = random.sample(range(1,100),30)
    print "gen the arr:",a
    print "search data: ",10
    print "result:  ",bin_search(a,10,0,len(a))
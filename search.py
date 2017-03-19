#coding:utf-8


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

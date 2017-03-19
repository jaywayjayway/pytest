#coding:utf-8
import random

## 快排 ##
def qsort(arr):
    if not arr:
        return []
    prio= arr[0]
    less = [ i for  i in  arr if  prio > i ]
    more = [ i for  i in  arr[1:] if prio <= i ]

    return qsort(less)+[prio]+qsort(more)

##  shell排序  ##
def shell_sort(ary):
    n = len(ary)
    gap = int(round(n/2))
    while gap > 0 :
        for i in range(gap,n):
            temp = ary[i]
            j = i
            while ( j >= gap and ary[j-gap] > temp ):
                ary[j] = ary[j-gap]
                j = j - gap
            ary[j] = temp
        print ary
        gap = int(round(gap/2))
    return ary


## 插入排序 ##
def insert_sort(ary):
    n = len(ary)
    for i in range(1,n):
        if ary[i] < ary[i-1]:
            temp = ary[i]
            index = i
        for j in range(i-1,-1,-1):
            if ary[j] > temp :
                ary[j+1] = ary[j]
                index = j
            else :
                break
            ary[index] = temp
    return ary




## 冒泡排序 ##
def bubble_sort(arr):

    n = len(arr)
    for i in range(n):
        flag = 1
        for j in range(1,n-i):
            if  arr[j] < arr[j-1]:
                arr[j-1],arr[j] = arr[j],arr[j-1]
        if not flag:
            return arr

    return arr


## 归并排序 ##
def merge_sort(ary):
    if len(ary) <= 1 : return ary
    num = int(len(ary)/2)       #二分分解
    left = merge_sort(ary[:num])
    right = merge_sort(ary[num:])
    return merge(left,right)    #合并数组

def merge(left,right):
    '''合并操作，
    将两个有序数组left[]和right[]合并成一个大的有序数组'''
    l,r = 0,0           #left与right数组的下标指针
    result = []
    while l<len(left) and r<len(right) :
        if left[l] < right[r]:
            result.append(left[l])
            l += 1
        else:
            result.append(right[r])
            r += 1
    result += left[l:]
    result += right[r:]
    return result


if __name__ == '__main__':
    a = random.sample(range(1,100),19)
    print "befort sort is ",a
    print "shell sort is ",shell_sort(a)
    print "qsort is ",qsort(a)

    print "bubble sort  is",  bubble_sort(a)
    print "megrge sort is ",merge_sort(a)


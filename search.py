import random
def qsort(arr):
    if not arr:
        return []
    prio= arr[0]
    less = [ i for  i in  arr if  prio > i ]
    more = [ i for  i in  arr[1:] if prio <= i ]

    return qsort(less)+[prio]+qsort(more)


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

a = random.sample(range(1,100),19)

arr = qsort(a)
print shell_sort(a)
print "qsort is ",arr


brr = bubble_sort(a)
print "bubble sort  is", brr
print bin_search(arr,10,0,len(a))

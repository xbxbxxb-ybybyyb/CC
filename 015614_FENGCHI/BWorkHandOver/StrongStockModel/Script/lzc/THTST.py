# @Time : 2022/3/17 17:17
# @Author : Zhichen Lu
# @File : THTST.py

def binary_earch(val,lst):
    if not lst:
        return -1
    middle = len(lst)//2
    if lst[middle]==val:
        return middle

    elif lst[middle]>val:
        sub = binary_earch(val,lst[:middle-1])
        if sub==-1:
            return - 1
        else:
            return  middle - len(lst[:middle-1]) + sub+1
    else:
        sub = binary_earch(val,lst[middle+1:])
        if sub==-1:
            return -1
        else:
            return middle + sub +1

a = [2,3,4,5,6,7,8,9]
res = binary_earch(8,a)
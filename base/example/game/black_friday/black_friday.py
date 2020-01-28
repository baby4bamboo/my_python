#!/usr/bin/python
# -*- coding: UTF-8 -*-

#找出一年中哪些日子是“黑色星期五”
#一般，将一个日期恰好是13号的星期五称为“黑色星期五”。
import time
import datetime

my_year=int(input("Please input the year:"))

for i in range(1,1000):
    y, m, d = [my_year,1,1]
    new_day = str(datetime.datetime(y, m, d) + datetime.timedelta(i)).split()[0]

    t = time.strptime(new_day, "%Y-%m-%d")
    y, m, d = t[0:3]
    weekday=datetime.datetime(y, m, d).strftime("%w")
    
    if weekday=="5" and d==13 and y==my_year:
        print ("black Friday is :",str(datetime.datetime(y, m, d)).split()[0])






'''
def get_day_nday_after(date,n):
    print(date)
    t = time.strptime(date, "%Y,%m,%d")
    y, m, d = t[0:3]
    Date = str(datetime.datetime(y, m, d) + datetime.timedelta(n)).split()
    return Date[0]
a=get_day_nday_after('2020-1-1',200)
print(a)
'''
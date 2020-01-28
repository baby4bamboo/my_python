  #第 0012 题：敏感词文本文件 filtered_words.txt，当用户输入敏感词语，则用 星号 * 替换，例如当用户输入「北京是个好城市」，则变成「**是个好城市」。


import sys,os,time,re

filename="./base/example/string/filtered_words/filtered_words.txt"
fo=open(filename, 'r')
#print ("文件名: ", fo.name)
#print ("是否已关闭 : ", fo.closed)
#print ("访问模式 : ", fo.mode)
str = fo.read()

my_list=str.split("\n")
fo.close()

print ("读取的字符串是 : ", my_list)

my_str=input("请输入：")
print ("你输入的内容是: ", my_str)

for i in my_list:
    my_str.find(i) != -1
    my_str = re.sub(i, "**", my_str)
print(my_str)




    

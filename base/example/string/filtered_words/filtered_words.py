#第 0011 题：敏感词文本文件 filtered_words.txt，当用户输入敏感词语时，则打印出 Freedom ，否则打印出 Human Rights。


import sys,os,time

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
eq=0
for i in my_list:
    if i == my_str:
        eq = 1
        print("Freedom")
        
if eq == 0:
    print("Human Rights")
    

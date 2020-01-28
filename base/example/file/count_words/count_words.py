  #第 0004 题：任一个英文的纯文本文件，统计其中的单词出现的个数。

import sys,os,time,re

filename="./base/example/file/count_words/count_words.txt"
fo=open(filename, 'r')
my_str = fo.read()
my_str = re.sub("\n|,", " ", my_str)
my_article=my_str.split(" ")
fo.close()

my_dic={}

for i in my_article:
    if bool(re.search(r'[a-zA-Z]',i)):
        if i in my_dic:
            my_dic[i]=my_dic[i]+1
        else:
            my_dic[i]=1

for i in my_dic:
    #print(i)
    print(i+":"+str(my_dic[i]))
                




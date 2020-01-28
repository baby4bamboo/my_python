#第 0014 题： 纯文本文件 student.txt为学生信息, 里面的内容（包括花括号）
import pandas as pd
import numpy as np


my_dic = {
	"1":["张三",150,120,100],
	"2":["李四",90,99,95],
	"3":["王五",60,66,68]
}

df = pd.DataFrame(my_dic)
out_file="./base/example/excel/test2.xlsx"
df.to_excel(out_file,sheet_name='A')

df.columns = ['a','b','c']
df.to_excel(out_file,sheet_name='A')

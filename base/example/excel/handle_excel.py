import pandas as pd
import numpy as np

df = pd.read_excel(r'./base/example/excel/data.xlsx')
print(df.head())


writer = pd.ExcelWriter('./base/example/excel/new.xlsx')
#df2 = pd.DataFrame(data = df['column0']) #取出data的column[0]存入out.xlsx中
df.to_excel(writer, 'A', index = False) #只保存column[0]而没有index
writer.save()

out_file="./base/example/excel/test.xlsx"

A = np.array([[1,2,3],[4,5,6]])
df = pd.DataFrame(A)
df.to_excel(out_file,sheet_name='A')

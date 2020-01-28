#设定一个长度为 N 的数字串，将其分为两部分，找出一个切分位置，使两部分的乘积值最大，并返回最大值。

def product(input_str):
   
    number_length=len(input_str)
    my_list=[]

    for i in range(1,number_length):
        my_first=int(input_str[:i])
        my_second=int(input_str[i:])
        my_result=my_first * my_second
        my_list.append(my_result)

    print (max(my_list))

input_str=input("Please input the number:")
product(input_str)



    




    


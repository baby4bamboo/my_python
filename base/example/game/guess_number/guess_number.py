#猜数字游戏

from random import randint


my_str=input("Guess what i think ?  1-100 ")
i = 0
num = randint(1, 100)

while(i == 0):
    my_str=int(my_str)
    if my_str > num:
        print("Too big")
        my_str=input()
    elif my_str < num:
        print("Too small")
        my_str=input()
    elif my_str == num:
        print("Bingo !")
        i = 1

    


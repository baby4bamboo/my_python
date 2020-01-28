#罚点球游戏
#每一轮，你先输入一个方向射门，然后电脑随机判断一个方向扑救。方向不同则算进球得分，方向相同算扑救成功，不得分。
#之后攻守轮换，你选择一个方向扑救，电脑随机方向射门。
#第5轮结束之后，如果得分不同，比赛结束。
#5轮之内，如果一方即使踢进剩下所有球，也无法达到另一方当前得分，比赛结束。
#5论之后平分，比赛继续进行，直到某一轮分出胜负。

from random import randint

my_dic={
'my_score': 0 ,
'com_score': 0
}
i=1
while( i < 6) :
    my_num=int(input("rand1: 0,1,2 means left,mid,right,please guess:"))
    com_num = randint(0,2)
    if my_num != com_num:
        my_dic['my_score']+=1

    my_num=int(input("rand2: 0,1,2 means left,mid,right,please guess:"))
    com_num = randint(0,2)
    if my_num != com_num:
        my_dic['com_score']+= 1

    dif = abs(my_dic['my_score']- my_dic['com_score'])
    left_round = 5 - i
    if dif > left_round:
        print(dif)
        print(left_round)
        i=6
    
    if left_round == 0 and dif == 0:
        i=i-1

    i=i+1



print(my_dic)











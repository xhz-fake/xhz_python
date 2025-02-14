

"""
1:任意输入华氏温度，把华氏温度转变为摄氏温度并显示
"""

Ctem=int(input("请输入华氏温度"))
Ftem=9/5*Ctem+32
print("\n")
print("华氏温度为")
print(Ftem)

"""
2、、某公园要求年龄不超过6岁且身高不超过1.2米的儿童可以免费
游玩，否则要收100元门票，随意输入入园人姓名、年龄、身高，结果
为显示该入园人是否应该缴纳门票；
"""

age=int(input("请输入年龄"))
height=float(input("请输入身高"))
print("\n")
if age<=6 and height<=1.2:
    print("免费")
else:
    print("收费")

"""
3、某一高校评奖学金，评奖办法为：
1）采用百分制积分，得分高的获取奖学金；
2）具体得分语文、数学、英语三门课的平均成绩，加上成果得分；
3）成果：发表一篇论文加5分，申请一个专利加4分，获得的成果总加分不得超过30分；
4）报告要求：需要画出流程图；
5）程序要求，随机输入5名学生的姓名、三科的成绩、发表论文数量、申请专利数量。程序
   运行结果按顺序显示出一、二、三等奖姓名、得分；
注：不需要搭建数据库，5名学生数据用不同的变量。
"""

name1=input("请输入姓名")
chinese1=int(input("请输入1号语文成绩"))
math1=int(input("请输入1号数学成绩"))
english1=int(input("请输入1号英语成绩"))
paper1=int(input("请输入1号发表论文数量"))
patent1=int(input("请输入1号申请专利数量"))
name2=input("请输入姓名")
chinese2=int(input("请输入2号语文成绩"))
math2=int(input("请输入2号数学成绩"))
english2=int(input("请输入2号英语成绩"))
paper2=int(input("请输入2号发表论文数量"))
patent2=int(input("请输入2号申请专利数量"))
name3=input("请输入姓名")
chinese3=int(input("请输入3号语文成绩"))
math3=int(input("请输入3号数学成绩"))
english3=int(input("请输入3号英语成绩"))
paper3=int(input("请输入3号发表论文数量"))
patent3=int(input("请输入3号申请专利数量"))
name4=input("请输入姓名")
chinese4=int(input("请输入4号语文成绩"))
math4=int(input("请输入4号数学成绩"))
english4=int(input("请输入4号英语成绩"))
paper4=int(input("请输入4号发表论文数量"))
patent4=int(input("请输入4号申请专利数量"))
name5=input("请输入姓名")
chinese5=int(input("请输入5号语文成绩"))
math5=int(input("请输入5号数学成绩"))
english5=int(input("请输入5号英语成绩"))
paper5=int(input("请输入5号发表论文数量"))
patent5=int(input("请输入5号申请专利数量"))

ave1=(chinese1+math1+english1)/3
score1=ave1+paper1*5+patent1*4
ave2=(chinese2+math2+english2)/3
score2=ave2+paper2*5+patent2*4
ave3=(chinese3+math3+english3)/3
score3=ave3+paper3*5+patent3*4
ave4=(chinese4+math4+english4)/3
score4=ave4+paper4*5+patent4*4
ave5=(chinese5+math5+english5)/3
score5=ave5+paper5*5+patent5*4

teams={
    "name1":score1,
    "name2":score2,
    "name3":score3,
    "name4":score4,
    "name5":score5
}

sorted_teams = sorted(teams.items(), key=lambda x: x[1], reverse=True)
top_three_teams = sorted_teams[:3]
print("\n")
print("一二三等奖为:")
for team, count in top_three_teams:
    print(f"{team}: {count}")
























import random
"""
#复合定义
arr=[i for i in range(1,10) if i%2==0]
print(arr)
#元组
tu=(123,456,789,[3334],"牛逼")

print(tu,type(tu))
print (tu[4])

a,b,*c=tu
print(a)
print(b)
print(*c)

#字典
dic={"name":"张三","age":18,"sex":"男"}
print (dic["name"],dic["age"],dic["sex"])
for i in dic:
    print(i,dic[i])
res=dic.get("wife","光棍一个")
res2=dic.get("name")
print(res,res2)

res3=dic.setdefault("hobby","吃粑粑")
print(res3)
print(dic)
dic .update({"name":"李四","特点":"起飞"})
print(dic)
dic.pop("特点")
print(dic)

dic.popitem()
print(dic)

ans=dic.items()
print(ans)
ans2=dic.keys()
print(ans2)
ans3=dic.values()
print(ans3)

#集合
set1=set()
print(type(set1))
set1={1,2,3,4,5,6,7,8,9}
print(set1,type(set1))
set1.add("宝贝")
print(set1)
set1.remove(1)
print(set1)
set1.pop()
print(set1)
set1.update({1,2})
print(set1)
set1.clear()
print(set1)
set1={1,2,3,4,5,6,7,8,9}
set2={1,2,3,4,5,6,7,8,9,10}
res=set1&set2
print(res)
res2=set1|set2
print(res2)
res3=set2.isdisjoint(set1)
print(res3)
"""
###############################################################################3
str="iamxhzniubiPLUS"
str=str.lower()
dit={char:0 for char in "abcdefghijklmnopqrstuvwxyz"}
for char in str:
    if char in dit:
        dit[char]+=1

for char, count in dit.items():
    if count>0:
        print(f"{char}:{count}",end=" ")

print("\n")

################################################################################

str1="123456789abcdefghijklmnopqrstuvwxyz"
for i in range(10):
        ans=random.choices(str1,k=8)
        print("第%d个密码是：%s"%(i+1,ans))

##################################################################################3

print("请输入你的电话号码：\n")
num=input()
for i in range(1,len(num)):
    if num[i].isdigit()==False:
        print("请输入11位阿拉伯数字\n")
        break
    else:
        if len(num)!=11:
            print("请输入11位数字\n")
        else:
            if num[0]!="1":
                print("请输入以“1”开头的号码\n")
            else:
                print("输入正确！你的号码是：",num)
        break
######################################################################################

























import keyword
import decimal
print(keyword.kwlist)
print(dir(__builtins__))
"""
n=int(input("请输入\n"))
n2=int(input("请输入\n"))
ans=int(n)+int(n2)
print("和是",ans)
"""
"""
print(f'我在{2025}年{1}月{10}日开始{"python"}的学习')
n1=input("第一个\n")
n2=input("第二个\n")
ans=decimal.Decimal(str(n1))-decimal.Decimal(str(n2))
print(ans)
"""
r=input("请输入半径\n")
area=decimal.Decimal(str(3.1415926))*decimal.Decimal(str(r))**2
c=decimal.Decimal(str(2))*decimal.Decimal(str(3.1415926))*decimal.Decimal(str(r))
print("圆的周长为%.2f,面积为%.2f" %(c,area))

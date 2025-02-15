import time
import random

class Account:
    def __init__(self, name, password, money=0):
        self.name = name
        self.money = money
        self.password=password

        t=int(time.time()*100)
        r=random.randint(10,99)
        self.number=str(t)+str(r)

    def savemoney(self,money):
        self.money += money

    def withdraw(self,money):
        self.money -= money

    def check(self):
        print(f"账户{self.number}的当前余额为{self.money}")

    def __del__(self):
        print(f" 卡号为{self.number}的{self.name}已销户")
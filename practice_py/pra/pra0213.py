
class Account:
    def __init__(self,account_holder,initial_balance=0):
        self.account_holder=account_holder
        self.balance=initial_balance
        self.is_active=True
        self.livingsituation=True

    def deposit(self,amount):
        if self.is_active:
            if amount>0:
                self.balance+=amount
                print(f"存款成功!账户{self.account_holder}的当前余额为{self.balance}")
            else:
                print("存款金额必须大于0")
        else:
            print("账户已销户,无法进行存款操作")

    def withdraw(self,amount):
        if self.is_active:
            if amount>0 and amount<=self.balance:
                self.balance-=amount
                print(f"取款成功!账户{self.account_holder}的当前余额为{self.balance}")
            else:
                print(f"用户{self.account_holder}余额不足")
        else:
            print("账户已销户,无法进行取款操作")

    def check_balance(self):
        if self.is_active:
            print(f"经查验，账户{self.account_holder}的当前余额为{self.balance}")
        else:
            print("账户已销户,无法查看余额")

    def close_account(self):
        if self.is_active:
            self.is_active=False
            print(f"已将账户{self.account_holder}销户")
        else:
            print("账户已销户,无法重复销户")

account1=Account("Vivian",1000000000)
account2=Account("Lisa",99999999999999999)
account3=Account("maniubi",0)

account1.deposit(19800)
account2.deposit(61000)
account3.deposit(250)

account1.withdraw(99999999)
account2.withdraw(99500)
account3.withdraw(8888888888)

account1.check_balance()
account2.check_balance()
account3.check_balance()

account3.close_account()























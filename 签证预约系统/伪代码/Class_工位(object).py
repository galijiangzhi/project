class 日期工位(object): #供日期生产元使用的工位
    def __init__(self):
        self.寻找可以工作的账号
        self.工作(self,self.日期生产员)
    def 寻找可以工作的账号:
        self.日期生产员=找到的生产员
    def 登录工位中的账号：
        工作账号登录
    def 判断账号是否到期：
        判断账号登陆时间
    def 更换账号：
        更换不能使用的账号
    def 工作：
        while
            登录
            while
                self.判断账号是否到期
                if 没到期
                    调用 self.日期生产员.对应工作
                else 到期了
                    self.寻找可以工作的账号
                    self.登录工位中的账号
                    
class 时间工位(object): #供时间生产元使用的工位
'''
    时间生产员也需要提前登录
'''
    def __init__(self):
        self.寻找可以工作的账号
        self.工作(self,self.时分生产员)
    def 寻找可以工作的账号:
        self.时分生产员=找到的生产员
    def 登录工位中的账号：
        工作账号登录
    def 工作：
        登录
        调用 self.日期生产员.对应工作

class 用户工位 #供用户使用的座位
    def __init__()
    def 下单
        下单 
        if 下单成功
            关闭该用户工位 
    def 检查用户状态
        访问目标网站 返回用户状态
    def 重登录操作
    def 工作：
        while   
            if self.检查用户状态 == 掉线
                self.重登录操作

class 用户工位管理员: #将用户带到座位
    def 工作：
        查看数据库中未进入工位的订单
        开启工位 放入订单 修改数据库内的订单状态
        整理订单的时间字典
#! encoding:utf-8
#轮询间隔
NORMAL_INTERVAL = 20
#出现问题之后的紧急请求间隔
RUSH_INTERVAL = 1
#出现问题之后的紧急请求次数
RUSH_TIMES = 3
#同一个服务器，通知间隔是多少(避免每次轮询都发邮件)
DND_TIME = 1200


# mail_list = ['huji@le.com','sunwei3@le.com','jiasai@le.com','lijianzhong@le.com']
mail_list = ['sunwei3@le.com']

#请保证源主机可以ping通目标主机
servers_info = [['10.154.157.78','9001']
                ,['10.154.157.78','9002']
                ,['10.154.157.78','9005']
                ,['10.140.45.87','8330']
                ,['10.140.45.87','8340']
                ,['10.140.45.87','8341']
                ,['10.140.45.873','8341']
                 ]

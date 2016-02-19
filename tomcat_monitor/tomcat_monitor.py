#!encoding:utf-8
__author__ = 'irvingsun'
import socket
import re
import params
import dateUtil,time,mailUtil
from log import logger

pt = re.compile('HTTP/1.1')

SERVICES = params.servers_info
rush_interval = params.RUSH_INTERVAL
rush_times = params.RUSH_TIMES
mail_list = params.mail_list
interval = params.NORMAL_INTERVAL
dnd_time = params.DND_TIME
#已经发送邮件的服务器列表，元素格式为：
#{'server:port','sent_time'}
sent_list = {}

#
SUB = 'Tomcat服务监控'

# 调用失败文件正文内容
FAIL_CONTENT = '\
<HTML><HEAD></HEAD>\
<BODY>\
<H3>Hi, all:</H3>\
<p style="text-indent: 2em">\
您好，Tomcat监控服务报告:<font color="red"><b>调用失败</b></font>\
<div>服务信息: %s</div>\
<div>最后调用: %s</div>\
<br/>\
邮件为自动发送，请勿回复。\
</p>\
</BODY></HTML>\
'

class Monitor:
    def __init__(self):
        logger.info("----Tomcat服务监控-----")

    def visit(self, ip, port):
        clisocket = None
        try:
            clisocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clisocket.connect((ip, int(port)))
            clisocket.send("GET Tomcat HTTP/1.1\r\nHost:127.0.0.1\r\n\r\n")
            clisocket.settimeout(5)
            receive = clisocket.recv(100)
            result = pt.findall(receive)
            return len(result) == 1

        except Exception, e:
            print e
            return False

        finally:
            clisocket.close()

    def visit_rush(self,ip, port,times,interval):
        """
        连续多次访问服务器
        :param ip:
        :param port:
        :param times:
        :param interval:
        :return:  -1 全都失败； 0 有成功有失败； 1 全成功
        """
        result = []
        for i in xrange(times):
            res = self.visit(ip,port)
            if res not in result:
                result.append(res)
            time.sleep(interval)
        if len(result) == 2:
            return 0
        else:
            return 1 if result[0] else -1

    def monitor(self):
        server_infos = SERVICES
        for server in server_infos:
            key = ":".join(server)
            success = self.visit(server[0],server[1])
            logger.info(("调用成功" if success else '调用失败')+",服务器信息: "+key)
            #如果调用不成功
            if not success:
                #连续访问N次
                rush_result = self.visit_rush(server[0],server[1],rush_times,rush_interval)
                #如果连续访问都失败
                if rush_result is  -1:
                #查看是不是已经发送过邮件了，如果发送过则看是不是已经过了间隔了，发送邮件
                    sent_time = sent_list[key] if key in sent_list.keys() else None
                    if sent_time :
                        #如果超过免打扰时间
                        if long(sent_time) + int(dnd_time) < dateUtil.getCurrentTimeStamp():
                            #发送邮件,更新发送时间
                            #删除
                            sent_list.pop(key)
                            msg = FAIL_CONTENT % (key,dateUtil.getCurrentTime())
                            mailUtil.send_email(msg,SUB,mail_list)
                            logger.info("调用Tomcat出错，已发送邮件")

                        else:
                            logger.info("调用Tomcat出错，处于免打扰期，不发送邮件，需要等待")
                    #如果没有发送过邮件，则发送邮件，并且添加发送时间
                    else:
                        #添加
                        sent_list[key] = dateUtil.getCurrentTimeStamp()
                        msg = FAIL_CONTENT % (key,dateUtil.getCurrentTime())
                        mailUtil.send_email(msg,SUB,mail_list)
                        logger.info("调用Tomcat出错，已发送邮件")






if '__main__'== __name__:
    m = Monitor()
    while True:
        m.monitor()
        time.sleep(interval)

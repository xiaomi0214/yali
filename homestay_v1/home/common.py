#coding=utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import random
import string
import hashlib
import datetime

def getInter(price):
    try:
        price=int(price)
    except Exception as e:
        price=100

    return price

def sendEmail(email,emailContent):
    mail_host = "smtp.163.com"  # 设置服务器
    mail_user = "13772098509@163.com"  # 用户名
    mail_pass = "peng123456"  # 口令

    sender = mail_user
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText(emailContent, 'html', 'utf-8')
    message['From'] = sender
    message['To'] = receivers[0]
    print(message['From'],message['To'])
    subject = '彭芽丽民宿网站'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host,465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers[0], message.as_string())
        return True
    except Exception as e:
        return False

def getRandom(num=12):
    sting1=string.digits+string.ascii_letters
    result=""
    for i in range(20):
        result=result+random.choice(sting1)
    return result


def getPasswdHash(passwd):
    hashobj=hashlib.md5()
    hashobj.update(passwd)
    return hashobj.hexdigest()

def getNow():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__=="__main__":
    if sendEmail('mixiongxiong0214@163.com', "你好，欢迎使用彭的网站"):
        print ("ok")
    else:
        print ("not ")

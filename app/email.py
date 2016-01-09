import os
import smtplib  
from email.mime.text import MIMEText 
from flask import render_template

mail_host="smtp.qq.com"  #设置服务器
mail_user=os.environ['MAIL_USERNAME']#用户名
#test_environ=os.environ.get('MAIL_USERNAME')
mail_pass=os.environ['MAIL_PASSWORD']#口令"去qq邮箱开启SMTP服务获取密码" 
mail_postfix="qq.com"  #发件箱的后缀

def send_email(to_list,sub,template,**kwargs):  #to_list：收件人；sub：主题；content：邮件内容
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    content=render_template('auth/email/'+template+'.html',**kwargs)
    msg = MIMEText(content,_subtype='html',_charset='gb2312')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub    #设置主题
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        s = smtplib.SMTP()  
        s.connect(mail_host)  #连接smtp服务器
        print(me, to_list)        
        s.login(mail_user,mail_pass)  #登陆服务器  
        print(mail_user,mail_pass,'Login smtp server')              
        s.sendmail(me, to_list, msg.as_string())  #发送邮件
        print(mail_user[-1],type(mail_pass))
        s.close() 
        return True  
    except (Exception):            
        return False  
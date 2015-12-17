from flask import Flask,render_template,session,redirect,url_for,flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
import os
from flask.ext.script import Shell
from flask.ext.mail import Mail
from flask.ext.mail import Message
import smtplib  
from email.mime.text import MIMEText 
from threading import Thread 

#from flask.ext.migrate import Migrate,MigrateCommand

app=Flask(__name__)
#先声明app 再在下文中调用app参数
db=SQLAlchemy(app)
moment=Moment(app)
bootstrap=Bootstrap(app)
basedir=os.path.abspath(os.path.dirname(__file__))
manager=Manager(app)
#migrate=Migrate(app,db)
#migrate.add_command('db',MigrateCommand)
mail=Mail(app)

app.config['SECRET_KEY']='hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI']=\
	'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
mailto_list=["799611732@qq.com"] 
mail_host="smtp.163.com"  #设置服务器
mail_user=os.environ['MAIL_USERNAME']#用户名
test_environ=os.environ.get('MAIL_USERNAME')
mail_pass=os.environ['MAIL_PASSWORD']#口令 
mail_postfix="163.com"  #发件箱的后缀


def send_email(to_list,sub,content):  #to_list：收件人；sub：主题；content：邮件内容
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content,_subtype='html',_charset='gb2312')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub    #设置主题
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        s = smtplib.SMTP()  
        s.connect(mail_host)  #连接smtp服务器        
        s.login(mail_user,mail_pass)  #登陆服务器
        print(mail_user[-1],type(mail_pass))
        s.sendmail(me, to_list, msg.as_string())  #发送邮件
        s.close() 
        return True  
    except (Exception):            
        return False  

class NameForm(Form):
	name=StringField('What is your name ?',validators=[Required()])
	submit=SubmitField('Submit')

class Role(db.Model):
	__tablename__='roles'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(64),unique=True)
	users=db.relationship('User',backref='role')

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__='users'
	id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(64),unique=True,index=True)
	role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username

def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role)

manager.add_command("shell",Shell(make_context=make_shell_context))

#admin_role=Role(name='Admin')
#user_john=User(username='Bill',role=admin_role)
#db.session.add(admin_role)
#db.session.commit()



@app.route('/',methods=['GET','POST'])
def index():	
	#name=None
	#if form.validate_on_submit():
		#old_name=session.get('name')		
		#if old_name is not None and old_name != form.name.data:
			#flash('Looks like you have changed your name!')
		#session['name']=form.name.data
		#return redirect(url_for('index'))
	#return render_template('index.html',current_time=datetime.utcnow(),
		#form=form,name=session.get('name'))
	form=NameForm()
	if form.validate_on_submit():
		user=User.query.filter_by(username=form.name.data).first()		
		if user is None:
			user=User(username=form.name.data)
			db.session.add(user)
			session['known']=False
			print(mail_user)	
			print(test_environ)
			thr=Thread(target=send_email,args=[mailto_list,'New User','有新用户注册'])
			thr.start()
			#thr.join()		
			#send_email(mailto_list,'New User','有新用户注册')
		else:
			session['known']=True
		session['name']=form.name.data
		form.name.data=''
		return redirect(url_for('index'))
	return render_template('index_old.html',
		form=form,name=session.get('name'),
		current_time=datetime.utcnow(),
		known=session.get('known',False))

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'),500
#manager.run()
if __name__=='__main__':
	app.run(debug=True)


from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import login_user,login_required,logout_user,current_user
from . import auth
from ..models import User,Role,Post
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,\
					PasswordResetRequestForm,PasswordResetForm
from ..email import send_email
from .. import db
from threading import Thread
from werkzeug.utils import secure_filename
import os

upload_path='app\\static\\photos'
@auth.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password.')
	return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))

@auth.route('/register',methods=['POST','GET'])
def register():
	form=RegistrationForm()
	if form.validate_on_submit():
		f=request.files['photo']
		f_name=secure_filename(f.filename)
		f_type=f_name.split('.')[1]
		avatar_name=form.username.data+'.'+f_type
		avatar_path='photos/'+avatar_name
		avatar_upload_path=os.path.join(upload_path,avatar_name)
		user=User(email=form.email.data,
					username=form.username.data,
					password=form.password.data,
					avatar=avatar_path)
		db.session.add(user)
		db.session.commit()		
		f.save(avatar_upload_path)
		token=user.generate_confirmation_token()
		send_email([user.email],'Confirm your account',
			'confirm',user=user,token=token)		
		flash('A confirmation email has been sent to you by email.')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account, Thanks!')
	else:
		flash('The confirmation link is invalid pr has expired')
	return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
			and request.endpoint[:5]!='auth.' \
			and request.endpoint!='static':
			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/email/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
	token=current_user.generate_confirmation_token()
	send_email([current_user.email],'Confirm your account',
			'confirm',user=current_user,token=token)	
	flash('A new confirmation email has been sent to you by email')
	return redirect(url_for('main.index'))

@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
	form=ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password=form.password.data
			db.session.add(current_user)
			db.session.commit()
			flash('Your password has been updated!')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid password.')
	return render_template('auth/change_password.html',form=form)

@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form =PasswordResetRequestForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user:
			token=user.generate_reset_token()
			send_email([user.email],'Reset Your Password',
				'reset_password',user=user,token=token,
				next=request.args.get('next'))
		flash('An email with instructions to reset your password has been '
              'sent to you.')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
	#if not current_user.is_anonymous:
		#return redirect(url_for('main.index'))
	form=PasswordResetForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token,form.password.data):
			flash('Your password has been updated')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html',form=form)








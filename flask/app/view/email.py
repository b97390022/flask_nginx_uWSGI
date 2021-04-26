from flask import Flask, current_app, render_template, request, session, Blueprint, make_response, flash, url_for, redirect
from flask_mail import Mail, Message
from threading import Thread

class email(Mail):
    def send_confirm_email(self, app, **kwargs):

        template='auth/mail/activate'

        msg = Message(
            subject='Activate your account',
            recipients=[kwargs['user'].user_email]
            
        )
        msg.html = render_template(template + '.html', kwargs = kwargs)

        #  使用多線程
        thr = Thread(target=self.send_async_email, args=[app, msg])
        thr.start()
        return 
        
    # 非同步寄送email
    def send_async_email(self, app, msg):
        with app.app_context():
            self.send(msg)

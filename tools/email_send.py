#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : email_send.py
Description      : 
Time             : 2022/02/22 16:55:53
Author           : AllenLuo
Version          : 1.0
'''
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from tools.read_file import ReadFile
import time
from tools import logger

def email_send(subject, email_content):
    """
    
    Description: Email send method
    ---------
    Arguments:  subject - email subject, email_content - email body
    --------- 
    Returns:  
    -------
    
    """
    emai_config = ReadFile.read_config('$.emai')
    sender = emai_config['sender']
    receivers = emai_config['receivers']  # Recipient email addresses (QQ mail or others)
    # Three parameters: text content, 'plain' format, 'utf-8' encoding
    message = MIMEText(email_content, 'plain', 'utf-8')
    message['From'] = Header(sender, 'utf-8')   # Sender
    message['Subject'] = Header(subject, 'utf-8')
        # Recipient
    try:
        smtpObj = smtplib.SMTP(emai_config['mail_host'])
        for receiver in receivers:
            message['To'] =  Header(receiver, 'utf-8')
        smtpObj.sendmail(sender, receivers, message.as_string())
        return logger.info(f'Email sent successfully, recipients: {receivers}')
    except smtplib.SMTPException as e:
        return logger.error(f'Email send failed - {e}')

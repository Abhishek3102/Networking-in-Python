import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()  

with open('password.txt', 'r') as f:
    password = f.read().strip()

server.login('ankushpan694@gmail.com', password)

msg = MIMEMultipart()
msg['From'] = 'ankushpan694@gmail.com'
msg['To'] = 'betterpandey@gmail.com'
msg['Subject'] = 'Just a text'

with open('message.txt', 'r') as f:
    message = f.read()

msg.attach(MIMEText(message, 'plain'))

filename = 'Prepnudge.png'
attachment = open(filename, 'rb')

p = MIMEBase('application', 'octet-stream')
p.set_payload(attachment.read())

encoders.encode_base64(p)
p.add_header('Content-Disposition', f'attachment; filename = {filename}')
msg.attach(p)

text = msg.as_string()
server.sendmail('ankushpan694@gmail.com', 'betterpandey@gmail.com', text)
server.quit()

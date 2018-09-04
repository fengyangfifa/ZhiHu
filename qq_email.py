import threading
from email.mime.text import MIMEText
import smtplib
from email.utils import parseaddr, formataddr
from email.header import Header


class SendQQEmail(threading.Thread):
    def __init__(self, content, send_from, to_list):
        self.content = content
        self.send_from = send_from
        self.to_list = to_list
        threading.Thread.__init__(self)

    # 执行start时自动调用run函数
    def run(self):
        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr((Header(name, 'utf-8').encode(), addr))
        msg = MIMEText('%s' % self.content, 'plain', 'utf-8')
        msg['From'] = _format_addr('大西瓜 <%s>' % self.send_from)
        msg['Subject'] = Header('知乎每日邮件', 'utf-8').encode()
        password = '********'
        smtp_server = 'smtp.qq.com'
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.set_debuglevel(1)
        server.login(self.send_from, password)
        # 登录SMTP服务器
        server.sendmail(self.send_from, [self.to_list], msg.as_string())
        # as_string把MIMEText对象变成str, 列表表示一次可以发送多个邮件
        server.quit()


def send_qq_email(content, to_list):
    send_from = '*****@qq.com'
    sendemail = SendQQEmail(content, send_from, to_list)
    sendemail.start()


def send():
    try:
        with open('content.txt', 'r') as f:
            text = f.read()
            send_qq_email(text, '******@qq.com')
    except:
        pass

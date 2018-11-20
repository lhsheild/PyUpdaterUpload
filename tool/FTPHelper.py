import ftplib
import sys

CONST_HOST = "192.168.8.171"
CONST_USERNAME = "Administrator"
CONST_PWD = "Gut102015"
CONST_BUFFER_SIZE = 8192


class MyFtp(ftplib.FTP):
    def __init__(self, ftp_host=CONST_HOST, ftp_port=21, ftp_username=CONST_USERNAME, ftp_password=CONST_PWD):
        super().__init__()
        self.encoding = 'GBK'
        self.ftp_host = ftp_host
        self.ftp_port = ftp_port
        self.ftp_username = ftp_username
        self.ftp_password = ftp_password

    def ftp_login(self):
        try:
            self.connect(self.ftp_host, self.ftp_port, 3)
            print(self.welcome)
        except Exception as e:
            print('连接失败：', e)
        try:
            self.login(self.ftp_username, self.ftp_password)
            print('已登录FTP服务器')
            return 1000
        except Exception as e:
            print('登录失败：', e)

    def ftp_disconnect(self):
        try:
            self.quit()
            print('断开连接')
        except Exception as e:
            print(e)

    def ftp_getfiles(self, path=''):
        try:
            self.dir(path)
            list_file = self.nlst(path)
            return list_file
        except Exception as e:
            print("查看目录失败：", e)

    def upload_file(self, remote_path, local_path):
        try:
            buf_size = 8192
            fp = open(local_path, 'rb')
            self.storbinary('STOR ' + remote_path, fp, buf_size)
            self.set_debuglevel(0)
            fp.close()
            self.quit()
            return 1000
        except Exception as e:
            print('上传失败：', e)
            return 1001


class MyFtpTest(ftplib.FTP):
    def __init__(self):
        super(MyFtpTest, self).__init__()

    def connect_ftp(self, remote_ip, remote_port, login_name, login_password):
        my_ftp = MyFtp()

        try:
            my_ftp.connect(remote_ip, remote_port, 600)
            print('connect success')
        except Exception as e:
            print(sys.stderr, "conncet failed1 - %s" % e)
            return 0, 'connect failed'
        else:
            try:
                my_ftp.login(login_name, login_password)
                print('login success')
            except Exception as e:
                print(sys.stderr, "login failed1 - %s" % e)
                return 0, 'login failed'
            else:
                print('return 1')
                return 1, my_ftp


if __name__ == '__main__':
    ftp = MyFtpTest()
    my_ftp = ftp.connect()

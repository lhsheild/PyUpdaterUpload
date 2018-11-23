import ftplib
import sys
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

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

    def download(self, remote_host, remote_port, login_name, login_password, remote_path, local_path):
        res = self.connect_ftp(remote_host, remote_port, login_name, login_password)

        if res[0] != 1:
            print >> sys.stderr, res[1]
            sys.exit()

        ftp = res[1]
        ftp.set_pasv(0)

        # dires = self.split_path(remote_path)
        # if dires[0]:
        #     ftp.cwd(dires[0])
        # remote_file = dires[1]
        # print(dires[0] + '' + dires[1])
        fsize = ftp.size(remote_path)
        if fsize == 0:
            return

        lsize = 0
        if os.path.exists(local_path):
            lsize = os.stat(local_path).st_size

        if lsize >= fsize:
            print('local file is bigger or equal remote file')
            return

        block_size = 1024 * 1024
        cmpsize = lsize
        ftp.voidcmd('TYPE I')
        conn = ftp.transfercmd('RETR ' + remote_path, lsize)
        lwrite = open(local_path, 'ab')
        while True:
            data = conn.recv(block_size)
            if not data:
                break
            lwrite.write(data)
            cmpsize += len(data)
            print('download process:{}'.format(float(cmpsize)/fsize*100))

        lwrite.close()
        ftp.voidcmd('NOOP')
        ftp.voidresp()
        conn.close()
        ftp.quit()

    def upload(self, remote_host, remote_port, login_name, login_password, remote_path, local_path, callback=None):
        if not os.path.exists(local_path):
            print('local file is not exists')
            return
        self.set_debuglevel(2)
        res = self.connect_ftp(remote_host, remote_port, login_name, login_password)
        if res[0] != 1:
            print(res[1])
            sys.exit()
        ftp = res[1]
        remote = self.split_path(remote_path)
        ftp.cwd(remote[0])
        rsize = 0
        try:
            rsize = ftp.size(remote_path)
        except:
            pass
        if rsize == None:
            rsize = 0
        lsize = os.stat(local_path).st_size
        print('rsize:{}, lsize:{}'.format(rsize, lsize))
        if rsize == lsize:
            print('remote filesize is equal with local')
            return
        if rsize < lsize:
            local_file = open(local_path, 'rb')
            local_file.seek(rsize)
            ftp.voidcmd('TYPE I')
            datasock = ''
            esize = ''
            try:
                print(remote_path)
                datasock, esize = ftp.ntransfercmd('STOR ' + remote_path, rsize)
            except Exception as e:
                print(sys.stderr, '----------ftp.ntransfercmd-------- : %s' % e)
                return
            cmpsize = rsize
            while True:
                buf = local_file.read(1024 * 1024)
                if not len(buf):
                    print('no data break')
                    break
                datasock.sendall(buf)
                if callback:
                    callback(buf)
                cmpsize += len(buf)
                print('uploading {}'.format(float(cmpsize)/lsize*100))
                if cmpsize == lsize:
                    print('remote file size equal break')
                    break
            datasock.close()
            print('close data handle')
            local_file.close()
            print('close local file handle')
            ftp.voidcmd('NOOP')
            print('keep alive cmd success')
            ftp.voidresp()
            print('No loop cmd')
            ftp.quit()

    def split_path(self, remote_path):
        remote_path = os.path.abspath(remote_path)
        position = remote_path.rfind('/')
        return remote_path[:position + 1], remote_path[position + 1:]


class MyQThreadFTP(QThread, MyFtpTest):
    signal_server_unable = pyqtSignal(str)
    signal_server_bigger = pyqtSignal()
    signal_server_process = pyqtSignal(float)
    signal_upload_finish = pyqtSignal()

    def __init__(self, remote_host, remote_port, login_name, login_password, remote_file, local_file, is_upload):
        super().__init__()
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.login_name = login_name
        self.login_password = login_password
        self.remote_file = remote_file
        self.local_file = local_file
        self.is_upload = is_upload

    def __del__(self):
        self.wait()

    def run(self):
        if self.is_upload:
            self.upload_file()
        else:
            self.download_file()

    def download_file(self):
        res = self.connect_ftp(self.remote_host, self.remote_port, self.login_name, self.login_password)

        # 链接不上服务器则退出
        if res[0] != 1:
            print(sys.stderr, res[1])
            self.signal_server_unable.emit(res[1])

        ftp = res[1]
        ftp.set_pasv(0)

        remote_size = ftp.size(self.remote_file)
        if remote_size == 0:
            return

        local_size = 0
        if os.path.exists(self.local_file):
            local_size = os.stat(self.local_file).st_size

        if local_size >= remote_size:
            print('local file is bigger than remote file')
            self.signal_server_bigger.emit()
            return

        block_size = 1024 * 1024
        cmpsize = local_size
        ftp.voidcmd('TYPE I')
        conn = ftp.transfercmd('RETR ' + self.remote_file, local_size)
        local_writer = open(self.local_file, 'ab')
        while True:
            data = conn.recv(block_size)
            if not data:
                break
            local_writer.write(data)
            cmpsize += len(data)
            print('download process:{}'.format(float(cmpsize) / remote_size * 100))
            self.signal_server_process.emit(float(cmpsize) / remote_size * 100)

        local_writer.close()
        ftp.voidcmd('NOOP')
        ftp.voidresp()
        conn.close()
        ftp.quit()
        self.signal_upload_finish.emit()  # 上传完成

    def upload_file(self):
        if not os.path.exists(self.local_file):
            print('local file is not exixts')
            return
        self.set_debuglevel(2)
        res = self.connect_ftp(self.remote_host, self.remote_port, self.login_name, self.login_password)
        if res[0] != 1:
            print(res[1])
            self.signal_server_unable.emit(res[1])
            return
        ftp = res[1]



if __name__ == '__main__':
    ftp_client = MyFtpTest()
    # ftp_client.upload('192.168.0.176', 21, 'Administrator', 'Gut102015',
    #                   'cn_visual_studio_enterprise_2015_with_update_3_x86_x64_dvd_8923298.iso',
    #                   'D:/Software/cn_visual_studio_enterprise_2015_with_update_3_x86_x64_dvd_8923298.iso')

    ftp_client.download('192.168.0.176', 21, 'Administrator', 'Gut102015',
                        'cn_visual_studio_enterprise_2015_with_update_3_x86_x64_dvd_8923298.iso',
                        'd:/cn_visual_studio_enterprise_2015_with_update_3_x86_x64_dvd_8923298.iso')
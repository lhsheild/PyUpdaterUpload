import hashlib
import os
import os.path
import sys
import time

folder_size_dic = {}
file_md5_dic = {}

"""装饰器"""


def get_func_runtime(f):  # 计算函数运行时间
    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> RUN TIME: <%s> : %s' % (f.__name__, time.time() - s))
        return res

    return fi


class MyMD5(object):
    def __init__(self, dirpath='', filepath=''):
        super().__init__()
        self.dir_path = dirpath
        self.file_name = filepath

    def generate_md5_hash_for_dir(self, dir_path, block_size=2 ** 20, progress_blocks=128):
        """This function generates an md5 hash for a given floder."""

        file_md5_dic = {}
        for parent, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                file = os.path.join(parent, filename)  # 文件绝对路径
                file_relative_path = file.lstrip(os.path.join(dir_path, '\\')).rstrip(filename)  # 文件相对路径
                md5 = self.generate_md5_hash_for_file(file)  # 文件MD5
                file_md5_dic[filename] = [file_relative_path, md5]
        return file_md5_dic

    def generate_md5_hash_for_file(self, file_name, block_size=2 ** 20, progress_blocks=128):
        """This function generates an md5 hash for a given file."""

        md5 = hashlib.md5()
        global blocks, total_blocks
        blocks = 0
        total_blocks = 1 + (os.path.getsize(file_name) / block_size)
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(block_size)
                if not data:
                    break
                md5.update(data)
                # Display progress in the command line
                if (blocks % progress_blocks) == 0:
                    percentage_string = "{0}%".format(100 * blocks / total_blocks)
                    return str(100 * blocks / total_blocks)
                    sys.stdout.write("\r{1:<10}{0}".format(file_name, percentage_string))
                    sys.stdout.flush()
                blocks += 1
        return md5.hexdigest()

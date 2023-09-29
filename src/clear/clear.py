
import os
import shutil

OUTPUT_ROOT = "./output"

COUNT_FILE = "./count.txt"
PUB_COUNT_FILE = "./pub_count.txt"

if __name__ == '__main__':

    with open(COUNT_FILE, "w", encoding="utf8") as file:
        file.write("0")
    with open(PUB_COUNT_FILE, "w", encoding="utf8") as file:
        file.write("0")

    shutil.rmtree(OUTPUT_ROOT)
    os.mkdir(OUTPUT_ROOT)

# TODO: [君扬] 给Generator添加一个clear函数，用于清除生成的文件，该脚本的作用在于调用这个clear函数
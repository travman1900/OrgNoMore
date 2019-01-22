from pathlib import *
import re
import shutil
import os

#Notes  monitored directories
src_dir = r"C:\TestA"
dst0_dir = r"C:\TestB"
dst1_dir = r"C:\TestC"

#this notates that i want to look for "S" and " - " as delimiters ##i think###
season = re.compile(r'(.*?)\s?\-\s?S(\d+)')

for path in Path(src_dir).glob("**/*.txt"):
        data = season.match(path.name)
        if data:
            sname, snum = data.groups()
            dst = os.path.join(dst0_dir, sname, "Season "+snum)
            os.makedirs(dst)
        try:
                os.rename(path,os.path.join(dst,path.name))
        except:
                pass
        
        else:
                dst1 = os.path.join(dst1_dir,path.stem)
                os.makedirs(dst1)
        try:
                os.rename(path,os.path.join(dst1, path.name))
        except:
                pass

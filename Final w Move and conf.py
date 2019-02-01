from pathlib import Path
import re
import shutil
import os
import configparser

###src_dir = r"M:\DVR\Complete"
###dst1_dir = r"M:\TV Shows"
###dst2_dir = r"M:\Movies"

config = configparser.ConfigParser()
config.read('config.ini')

src_dir = config['DEFAULT']['source directory']
dst1_dir = config['DEFAULT']['destination1 directory']
dst2_dir = config['DEFAULT']['destination2 directory']

season = re.compile(r'(.*?)\s?\-\s?S(\d+)')
#looks for mkv and copy to new dir
for path in Path(src_dir).glob("**/*.mkv"):
    data = season.match(path.name)
    if data: # it matched the episode pattern
        sname, snum = data.groups()
        # make the dst folder
        dst = os.path.join(dst_dir, sname, "Season "+snum)
        os.makedirs(dst1)
        shutil.move(str(path), str(dst1))
    else: #this is here to copy movies as they shouldnt follow ^ naming convention
        dst1 = os.path.join(dst1_dir, path.stem)
        os.makedirs(dst1, exist_ok=True)
        shutil.move(str(path), str(dst1))
#looks for srt and copy to new dir
for path in Path(src_dir).glob("**/*.srt"):
    data = season.match(path.name)
    if data: # it matched the episode pattern
        sname, snum = data.groups()
        # make the dst folder
        dst = os.path.join(dst2_dir, sname, "Season "+snum)
        ## os.makedirs(dst, exist_ok=True)
        shutil.move(str(path), str(dst2))
    else:  #this is here to copy movies as they shouldnt follow ^ naming convention
        dst1 = os.path.join(dst1_dir, path.stem)
        ## os.makedirs(dst1, exist_ok=True)
        shutil.move(str(path), str(dst2))

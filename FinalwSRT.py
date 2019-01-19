from pathlib import Path
import re
import shutil
import os

src_dir = r"C:\TestA"
dst_dir = r"C:\TestB"
dst1_dir = r"C:\TestC"

season = re.compile(r'(.*?)\s?\-\s?S(\d+)')

for path in Path(src_dir).glob("**/*.mkv" and "**/*.srt"):
    data = season.match(path.name)
    if data: # it matched the episode pattern
        sname, snum = data.groups()
        # make the dst folder
        dst = os.path.join(dst_dir, sname, "Season "+snum)
        os.makedirs(dst, exist_ok=True)
        shutil.copy(path, dst)
    else:
        dst1 = os.path.join(dst1_dir, path.stem)
        os.makedirs(dst1, exist_ok=True)
        shutil.copy(path, dst1)

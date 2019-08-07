from pathlib import Path
import re
import shutil
import os
import configparser
import subprocess
import datetime
import sys
import time
config = configparser.ConfigParser()
config.read('config.ini')



#source where this program should be looking for files
src_dir = config['DEFAULT']['source directory']
#destination of TV Shows for HTPC
shows_dir = config['DEFAULT']['shows directory']
#destination of Movies for HTPC
movies_dir = config['DEFAULT']['movies directory']
#This is currently set up in the INI for nfo jpeg srt and mkv. Substitute your media file type for MKV if different. I have not tested but if you follow format additonal types should be able to added.
file_type = config['DEFAULT']['file type']
#This is here to prevent the program from stumbling on it self during the move process. I have tested as low as 1 and as high as 5 with no issue. adding a decimal will make it Milliseconds
set_wait_timer = config ['DEFAULT']['wait timer']
#The regex is looking at filename IE (TVSHOW - S01E01 - Episode.mkv) Its look for S## after a -
season = re.compile(r'(.*?)\s?\-\s?[S|s](\d+)')

#looks for the file types from INI and copy to new dir
for path in Path(src_dir).glob(f"**/*{file_type}"):
    data = season.match(path.name)
    try:
        if data: #it matched the episode pattern
            sname, snum = data.groups()
            #make the destination folder
            shows = os.path.join(shows_dir, sname, "Season "+snum)
            os.makedirs(shows, exist_ok = True)
            shutil.move(str(path), str(shows))
            #waits an interval based on INI to prevent false positive duplicates
            time.sleep(int (set_wait_timer))

        else: #this is here to copy movies as they shouldnt follow ^ naming convention
            movies = os.path.join(movies_dir, path.stem)
            os.makedirs(movies)
            shutil.move(str(path), str(movies))
    except:
        #pulls current date 
        timestr = time.strftime("%Y%m%d")
        #notates the filename will be errorlogDATE.txt when called
        errorlog = "errorlog%s.txt" % timestr
        with open(str(errorlog) , 'a') as f:
            #provide insight as to what is a duplicate
            print ('I failed to move a file:',str(path),'Check for duplicates\n', file=f)

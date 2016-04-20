import glob, os
from stat import *
import time


# get the time stamp of the most recent jpeg in the output folder
newfile_timestamp = 0
newest_file = ""

# get the list of all files that are in the Outputs folder

try:
    while True:
        try:
            test = glob.glob('images/*.txt')
            print "Start"
            for name in test:
                st = os.stat(name)
                if st[ST_MTIME] > newfile_timestamp:    #ST_MTIME - last modified
                        newfile_timestamp = st[ST_MTIME]
                        newest_file = name
                        print newfile_timestamp
                        print newest_file
        finally:
            print "bugger"
            time.sleep(2)
finally:
    print "Keyboard exception"
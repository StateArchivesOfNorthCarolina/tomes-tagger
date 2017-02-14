import os
import shutil
import subprocess
import tempfile
import time
from glob import glob

# make plain text version of given file.
def convert(htm):
    if "#" in htm: # PhantomJS can't open files with hashtags, so using temp file.
        input_handle, input_file = tempfile.mkstemp(suffix=".html")
        shutil.copy(htm, input_file)
    else:
        input_file = htm
    output_file = htm + ".txt"
    cmd = "phantomjs html_to_text.js %s %s" %(input_file, output_file)
    subprocess.call(cmd)
    if input_file != htm: # delete temp file.
        os.close(input_handle)
        os.remove(input_file)

# start timer.
start = time.time()

# get html files; count number of files; convert files.
html_len = 0
for root, dirs, files in os.walk("."):
    for f in files:
        f = os.path.join(root, f)
        if f[len(f) - 5:] == ".html":
            convert(f)
            html_len += 1
    
# report processing time.
total_time = time.time() - start
if html_len == 0:
    print "No HTML files found."
    exit()
print "Processed %d files in %s seconds for an average of %s seconds per file." %(html_len, total_time, total_time/html_len)

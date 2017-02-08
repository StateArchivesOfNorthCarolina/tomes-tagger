from glob import glob
import subprocess
import time

start = time.time()

html = glob("*.html")
html_len = len(html)

for htm in html:
    cmd = "phantomjs html_to_text.js %s" %htm
    subprocess.call(cmd, shell=True)

total_time = time.time() - start
print "Processed %d files in %s seconds for an average of %s seconds per file." %(html_len, total_time, total_time/html_len)

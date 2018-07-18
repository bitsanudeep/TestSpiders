import sys,os,ntpath
# Enable the script to run from anywhere and have a good PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','imagesCrawler'))
import json
from subprocess32 import Popen, PIPE, CalledProcessError

# print json.dumps(sampleInput)

import logging
logger = logging.getLogger(__name__)
def create_json_safe_string(in_str):
    if in_str is None:
        return ''
    unicode_corrected_result = ''  
    for i in in_str:
       try:
          unicode_corrected_result += unicode(i)
       except UnicodeDecodeError:
          unicode_corrected_result+='?'
    return unicode_corrected_result

def crawl_and_capture(crawlCommand):
    ps = Popen(crawlCommand, stdout=PIPE, stderr=PIPE,cwd=os.path.dirname(os.path.abspath(__file__)))
    stdout, stderr = None, None
    try:
        stdout, stderr = ps.communicate()
        stdout = stdout.strip()
        print stdout
    except:
        raise Exception(stderr)

def crawl_and_yield(crawlCommand):
    ps = Popen(crawlCommand, stdout=PIPE, stderr=PIPE,cwd=os.path.dirname(os.path.abspath(__file__)))
    for stdout_line in iter(ps.stdout.readline, ""):
        print stdout_line 
    ps.stdout.close()
    return_code = ps.wait()
    if return_code:
        raise CalledProcessError(return_code, crawlCommand)

def usage():
    print("{} <file(s)/directory(s)> ".format(__file__))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        crawlConfig =  sys.argv[2]
        url =  sys.argv[3]
        crawlConfig=json.loads(crawlConfig)
        commandArr = ["scrapy","crawl",crawlConfig["crawlerName"],"-a","start_url={}".format(url) ]
        crawl_and_capture(commandArr)
    else:
        usage()
    exit(0)
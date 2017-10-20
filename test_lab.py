#!/usr/bin/env python

import optparse
import os
from common import http_receiver
import time
import sys
import json

def main():
    currFolder = os.path.dirname(os.path.abspath(__file__))
    defInFile = os.path.join(currFolder, "in", "list.txt")
    outJsonFile = os.path.join(currFolder, "out", "out.json")

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-j", action="store_true", default=False, help='Write the test output to a json file')
    parser.add_option("-u", "--useragent", type="str", default="Python http auth", help='User-Agent (default "Python http auth")')
    parser.add_option("-t", "--timeout", type="float", default=3, help='Set connection timeout (default 3)')
    parser.add_option("-f", "--filename", type="str", default=defInFile, help='Input file path (default %s)' % (defInFile))
    parser.add_option("-o", "--outfile", type="str", default=outJsonFile, help='Path to out file (default %s)' % (outJsonFile))
    (options, args) = parser.parse_args()

    t = options.timeout
    iFile = options.filename
    try:
       f = open(iFile, "r")
    except Exception:
       print("Can't open %s file" % (iFile))
       sys.exit(1)

    resDict = {}
    for line in f:
        tURL = line
        tURL = tURL.replace('\n', '')
        tURL = tURL.replace('\r', '')
        tURL = tURL.replace(' ', '')

        if len(tURL) > 0:
           headers = {"User-Agent": options.useragent}

           mObj = http_receiver.Receive(tURL, headers)
           resDict[tURL] = {}
           mObj.setdefaulttimeout(t)

           try:
              ip = None
              crTime = time.time()
              ip = mObj.find_connectable_ip()
              timeTaken = time.time() - crTime
              resDict[tURL][ip] = {'timeTaken': timeTaken}
              print("The time taken to establish a TCP connection to %s is %s:" % (ip, timeTaken))
           except Exception as ip_err:
              resDict[tURL]['IPError'] = str(ip_err)
              print(ip_err)

           if ip:
              for i in range(10):
                  res = mObj.urlopen()
                  if not res['object']:
                     resDict[tURL][mObj.url] = {'URLError': res['status']}
                     print(res['status'])
                     break

                  print("Opening URL=%s" % (mObj.url))
                  resDict[tURL][mObj.url] = {'status': res['object'].status}
                  print("Status is %s for URL=%s" % (res['object'].status, res['object'].url))

                  if res['object'].status in (301, 302, 303, 307):
                     mObj.url = res['object'].url

                  if res['object'].status == 200:
                     crTime = time.time()
                     data = res['object'].read()
                     timeTaken = time.time() - crTime
                     resDict[tURL][res['object'].url]['timeForData'] = timeTaken
                     print("The time taken for getting content is %s:" % (timeTaken))
                     break

                  res['object'].close()

           resDict[tURL]['redirectsNumber'] = mObj.sHandler.i
           print('The number of redirects is %s' % (mObj.sHandler.i))

    f.close()

    if options.j:
       iFile = options.outfile
       try:
          f = open(iFile, "w")
       except Exception:
          print("Can't open %s file for writing" % (iFile))
          sys.exit(1)

       jVal = json.dumps(resDict)
       f.write(jVal)
       f.close()

if __name__ == '__main__':
    main()
       

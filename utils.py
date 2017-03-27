import json
import os
import time
import urllib
import tempfile
import multiprocessing
import sys, traceback
from multiprocessing.pool import ThreadPool
from datetime import date
from datetime import datetime
import threading

from vk.exceptions import VkAPIError
from twocaptchaapi import TwoCaptchaApi

import psutil

def load_json(filename):
        try:
                data = json.load(open(filename))
        except:
                return None

        return data


def pretty_dump(data):
        return json.dumps(data, indent=4, separators=(',', ': '),ensure_ascii=False).encode('utf8')


def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate


rated_lock = multiprocessing.Lock()
json_lock = multiprocessing.Lock()
rated_queue =  multiprocessing.Queue()
_2captcha_api = None

@RateLimited(2.5)
def set_event():
    try:
        rated_lock.release()
    except ValueError:
        pass

def rl_dispatch():
    set_event()
    while True:
        rated_queue.get()
        set_event();

def run_ratelimit_dispatcher():
    p = multiprocessing.Process(target=rl_dispatch)
    p.start()

def init_2captcha(api_key):
    global _2captcha_api
    _2captcha_api = TwoCaptchaApi(api_key)

cerror = 0

def solve_capthca(cfile):
    with open(cfile, 'rb') as captcha_file:
        captcha = _2captcha_api.solve(captcha_file)
        res = captcha.await_result()
        return res, captcha

manager = multiprocessing.Manager()
mmap = manager.dict({})

def read_minfo(method):
    json = load_json("./files/minfo.json")
    if json:
        return str(json.get(method,"no method info"))
    else: 
        return "no info at all"

def update_minfo(method, type, incr):
    with json_lock:
        json = load_json("./files/minfo.json")
        if not json:
           json = {"method":{"type":incr}}
        else:
           mmap = json.get(method, {})
           mmap[type] = mmap.get(type,0)+incr
           json[method] = mmap
        open("./files/minfo.json","w").write(pretty_dump(json))

def info_string(method, val ):
    return  datetime.now().strftime('%H:%M:%S') + "\t" + method + "\t" + str(os.getpid()) +"\t" + val + "\t"+read_minfo(method) +"\t"+str(threading.active_count())+"\n"

no_captcha = multiprocessing.Event()
no_captcha.set()

def rated_operation(operation, args):
    global cerror
    current_captcha = None

    rated_lock.acquire()
    rated_queue.put("Can unlock")

    this_captcha = False
    with open("api_history","a") as file:
        while True:
            try:

               process = psutil.Process(os.getpid())
       
               print time.time(), operation._method_name, process.memory_info().rss, process.memory_info().rss/1024.0/1024.0, cerror, threading.active_count()
               

               if not this_captcha and not no_captcha.is_set(): #captcha in progress, wait
                   no_captcha.wait()
                
               ret = operation(**args)
         
               update_minfo(operation._method_name, "success", 1)
               if args.get("captcha_key", None):
                   update_minfo(operation._method_name, "capthca_ok", 1)
                   file.write(info_string(operation._method_name, "CAPTCHA OK [{}]; balance [{}]".format(args.get("captcha_key",None),_2captcha_api.get_balance())))
               else:
                   file.write(info_string(operation._method_name, "OK"))
               no_captcha.set()
               return ret
            except VkAPIError as e:
                if e.code == 14:
                    if not _2captcha_api:
                      raise

                    this_captcha = True
                    no_captcha.clear()

                    if current_captcha:
                        current_captcha.report_bad()

                    temp_name = next(tempfile._get_candidate_names())
                    temp_name = "./files/{}.jpg".format(temp_name)
                    urllib.urlretrieve (e.captcha_img, temp_name)
                    try:
                        print "solving captcha ...",
                        res,current_captcha = solve_capthca(temp_name)
                        print "ok"
                    except:
                        print "Somthing bad in capthca solving"
                        continue
                    print "Solved captcha: ",res
                    update_minfo(operation._method_name, "captcha", 1)     
                    args.update({"captcha_sid":e.captcha_sid,"captcha_key":res})   
                    continue
                                          
                if e.code == 6:
                    print "------- To many req for sec, throttling", e
                    time.sleep(1)
                    update_minfo(operation._method_name, "throttle", 1)

                    file.write(info_string(operation._method_name, "THROTTLE"))
                    continue
                else:
                    update_minfo(operation._method_name, "error", 1)
                    file.write(info_string(operation._method_name, str(e)))
                    no_captcha.set()
                    raise


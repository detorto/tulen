import json
import time
import multiprocessing
import sys, traceback
def load_json(filename):
	try:
		data = json.load(open(filename))
	except:
		return None

	return data


def pretty_dump(data):
	return json.dumps(data, indent=4, separators=(',', ': '),ensure_ascii=False).encode('utf8')

import time
import threading
from functools import wraps
import sys
import os



import multiprocessing
from multiprocessing.pool import ThreadPool
threads = ThreadPool(16)
import time
import threading

from vk.exceptions import VkAPIError
import psutil
#@RateLimited(2)  # 2 per second at most

import time
import threading

from functools import wraps

lock = multiprocessing.Lock()
q=  multiprocessing.Queue()

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

@RateLimited(1)
def set_event():
    try:
        lock.release()
    except ValueError:
        pass

def time_manager():
    set_event()
    while True:
        q.get()
        set_event();

p = multiprocessing.Process(target=time_manager)
p.start()

cerror = 0
def rated_operation(operation, args):
    global cerror
    lock.acquire()
    q.put("Can unlock")

    ret = None
    while True:
        try:
            process = psutil.Process(os.getpid())
       
            print time.time(), operation._method_name, process.memory_info().rss, process.memory_info().rss/1024.0/1024.0, cerror

            return operation(**args)
        except VkAPIError as e:
            if e.code == 6:
                print "------- To many req for sec, throttling", e
                time.sleep(5)
                cerror+=1
                continue
            else:
                raise
        except:
            raise

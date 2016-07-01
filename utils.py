import json
import time

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

def rate_limited(max_per_second, mode='wait', delay_first_call=False):
    """
    Decorator that make functions not be called faster than

    set mode to 'kill' to just ignore requests that are faster than the
    rate.

    set delay_first_call to True to delay the first call as well
    """
    lock = threading.Lock()
    min_interval = 1.0 / float(max_per_second)
    def decorate(func):
        last_time_called = [0.0]
        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            def run_func():

                lock.release()
                ret = func(*args, **kwargs)
                last_time_called[0] = time.clock()
                return ret
            lock.acquire()
            elapsed = time.clock() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if delay_first_call:
                if left_to_wait > 0:
                    if mode == 'wait':
                        time.sleep(left_to_wait)
                        return run_func()
                    elif mode == 'kill':
                        lock.release()
                        return
                else:
                    return run_func()
            else:
                # Allows the first call to not have to wait
                if not last_time_called[0] or elapsed > min_interval:
                    return run_func()
                elif left_to_wait > 0:
                    if mode == 'wait':
                        time.sleep(left_to_wait)
                        return run_func()
                    elif mode == 'kill':
                        lock.release()
                        return
        return rate_limited_function
    return decorate

@rate_limited(3)  # 2 per second at most
def rated_operation(operation, args):
	return operation(**args)

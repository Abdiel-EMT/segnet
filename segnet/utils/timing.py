
import os
import json
import datetime

from functools import wraps
from time import time
from typing import Callable, Any

def time_this(f: Callable) -> Callable:
    """
      Code snippet taken from : https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator
      Modified to work on Python 3.7
      This simply wraps the function and takes the time it takes to compute on a single run. 
      
      One could log it and then perform statistical analysis, rather than using timeit which 
      disables the garbage collector.
    """
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        exec_time = te - ts
        print(f'func:{f.__name__} args:[{args}, {kw}] took: {exec_time:.4f} s')
        return result
    return wrap
##

def time_log(path_to_logfile: str = None) -> Callable:
    """
        Logs the time to compute a function.
        Logging is done using the json-lines format : http://jsonlines.org/
        
        Each log consists of :
        {
            "datetimeUTC": (Standard Greenwich time at function call),
               "function": (Name of the function that was called, given by function.__name__),
                   "args": (Values of positional arguments, if JSON-serializable
                           str(type(arg)) for each non-JSON-serializable argument),
                 "kwargs": (Idem, for keyword arguments),
                   "time": (Time required to execute the wrapped function, calculated as follows:
                            ts = time()
                            result = f(*args, **kw)
                            te = time()
                            exec_time = te - ts
                            )
        }
        
        Arguments :
            path_to_logfile : (optional) string containing a valid path to a logfile.
                              If no path is specified, it will generate a default path :
                              
                              "`pwd`/time_logs.jsonl"
                              pwd is obtained using Python's os module, i.e. os.path.realpath('.')
        
        Returns another decorator which will measure time needed to execute code.
    """
    if not path_to_logfile:
        path_to_logfile = os.path.join(os.path.realpath('.'), 'time_logs.jsonl')
    
    def timed(f: Callable):
        @wraps(f)
        def wrap(*args, **kw):
            ts = time()
            result = f(*args, **kw)
            te = time()
            exec_time = te - ts
            json_cast = lambda x: x if is_jsonable(x) else str(type(x))
            data = {
                "datetimeUTC": str(datetime.datetime.utcnow()),
                "function": f.__name__,
                "args": [json_cast(arg) for arg in args],
                "kwargs": {key:json_cast(kw[key]) for key in kw.keys()},
                "time": exec_time
            }
            with open(path_to_logfile, 'a') as log:
                log.write(json.dumps(data)+'\n')
            return result
        ##
        return wrap
    ##
    return timed
##

def is_jsonable(x: Any) -> bool:
    """
        Verify if object is JSON-serializable.
        
        Arguments:
                    x : Literally any Python object.
                    
        Returns:
                 True : If json.dumps(x) succeeds.
                False : If json.dumps(x) raises any kind of Exception.
    """
    try:
        json.dumps(x)
        return True
    except:
        return False
##

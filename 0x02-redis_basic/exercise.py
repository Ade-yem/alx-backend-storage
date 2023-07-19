#!/usr/bin/env python3
"""Redis cache creation"""

import redis
import uuid
from typing import List, Tuple, Union, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """ define a count_calls decorator that takes a single method Callable"""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """decorator to store the history of inputs and outputs for
    a particular function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function"""
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output
    return wrapper


def replay(method: Callable):
    """display the history of calls of a particular function"""
    r = redis.Redis()
    key = method.__qualname__
    count = r.get(key).decode("utf-8")
    inputs = r.lrange(key + ":inputs", 0, -1)
    outputs = r.lrange(key + ":outputs", 0, -1)
    print("{} was called {} times:".format(key, count))
    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(key, i.decode("utf-8"),
                                     o.decode("utf-8")))


class Cache:
    """redis caching"""
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushall()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """takes a data argument and returns a string"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes,
                                                          int, float]:
        """ convert the data back to the desired format"""
        data = self._redis.get(key)
        if not data:
            return None
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """converts data to str"""
        return self.get(key, lambda b: b.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        """converts data to int"""
        return self.get(key, int)

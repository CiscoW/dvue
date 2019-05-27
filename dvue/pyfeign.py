"""
定义一个类似Feign功能的装饰器

"""
import re
import types
import requests
from functools import wraps


class PyFeign(object):

    def __init__(self, root):
        self.root = root

    def __call__(self, cls):
        return self.decorator(cls)

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)

    def decorator(self, cls):
        @wraps(cls)
        def wrapper(*args, **kwargs):
            setattr(cls, "root", self.root)
            return cls(*args, **kwargs)

        return wrapper

    # 被装饰器装饰的函数中有默认参数时，需要将默认参数注入到新的方法中
    @staticmethod
    def get_func_default_parameter_value(func):
        # 针对 func(a, b=1, *, c) 类的情况此方法失效
        default_parameter_value = {}
        if func.__defaults__:
            for i in range(-1, -len(func.__defaults__) - 1, -1):
                default_parameter_value[func.__code__.co_varnames[i]] = func.__defaults__[i]

        return default_parameter_value

    # 对uri 的解析是通用的 封装在一个方法中
    @staticmethod
    def get_uri(path, **kwargs):
        # 此处的self是被装饰类的
        uri = path.format(**kwargs)
        params = re.findall(r'{(\w+)}', path)
        for param in params:
            del kwargs[param]
            # locals()[param] = kwargs.get(param)
        return uri, kwargs

    # 总方法
    @staticmethod
    def request(path):

        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                uri, kwargs = PyFeign.get_uri(path, **kwargs)
                url = self.root + uri

                default_parameter_value = PyFeign.get_func_default_parameter_value(func)

                return requests.request(url=url, **default_parameter_value, **kwargs)

            return wrapper

        return decorator

    # get方法
    @staticmethod
    def get(path):
        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                uri, kwargs = PyFeign.get_uri(path, **kwargs)
                url = self.root + uri

                default_parameter_value = PyFeign.get_func_default_parameter_value(func)

                return requests.get(url=url, **default_parameter_value, **kwargs)

            return wrapper

        return decorator

    # post方法
    @staticmethod
    def post(path):
        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                # 此处的self是被装饰类的
                uri, kwargs = PyFeign.get_uri(path, **kwargs)
                url = self.root + uri

                default_parameter_value = PyFeign.get_func_default_parameter_value(func)

                return requests.post(url=url, **default_parameter_value, **kwargs)

            return wrapper

        return decorator


"""
装饰器使用示例
"""


@PyFeign("http://127.0.0.1:8000/api")
class Test(object):

    @PyFeign.request("/show_books")
    def test_request(self):
        pass

    @PyFeign.get("/show_books")
    def test_get(self):
        pass

    @PyFeign.post("/add_book")
    def test_post(self, data):
        pass

    @PyFeign.get("/getBookNum/{book_name}")
    def get_book_num(self, book_name):
        pass


if __name__ == '__main__':
    import json

    test = Test()

    response_request = test.test_request(method='GET')
    print(response_request.text)
    response_get = test.test_get()
    print(response_get.text)
    response_post = test.test_post(data=json.dumps({"book_name": "未来简史"}))
    print(response_post.text)

    r = test.get_book_num(book_name="未来简史")
    print(json.loads(r.text))

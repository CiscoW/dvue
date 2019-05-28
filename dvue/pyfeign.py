"""
定义一个类似Feign功能的装饰器

"""
import re
import json
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

    # 被装饰器装饰的函数中有默认参数时，需要将默认参数注入到新的方法中. 获取没有默认参数的参数名
    @staticmethod
    def merge_params(func, uri_params, **kwargs):
        # 提取默认参数及其对应的值
        # 针对 func(a, b=1, *, c) 类的情况此方法失效
        default_parameter_value = {}

        # 有默认值的参数及其对应值提取
        if func.__defaults__:
            for i in range(-1, -len(func.__defaults__) - 1, -1):
                default_parameter_value[func.__code__.co_varnames[i]] = func.__defaults__[i]

        # 没有默认值的参数提取
        if func.__code__.co_varnames:
            if func.__defaults__:
                no_default_value_parameter = list(func.__code__.co_varnames[
                                                  0:len(func.__code__.co_varnames) - len(func.__defaults__)])

            else:
                no_default_value_parameter = list(func.__code__.co_varnames[0:len(func.__code__.co_varnames)])

            # 如果self在no_default_value_parameter中要移除
            if 'self' in no_default_value_parameter:
                no_default_value_parameter.remove('self')

            # 移除传递到uri上的参数
            for param in uri_params:
                no_default_value_parameter.remove(param)

        else:
            no_default_value_parameter = []

        # 扣除默认参数和传递到url上的参数外，no_default_value_parameter的长度应该是0 or 1
        # 因此在超出1时抛出异常
        assert len(no_default_value_parameter) <= 1
        #
        if len(no_default_value_parameter) == 1:
            data = {"data": json.dumps(kwargs.get(no_default_value_parameter[0]))}
            del kwargs[no_default_value_parameter[0]]
        else:
            data = {}

        merge_params = dict(kwargs, **default_parameter_value, **data)

        return merge_params

    # 对uri 的解析是通用的 封装在一个方法中
    @staticmethod
    def get_uri(path, **kwargs):
        uri = path.format(**kwargs)
        uri_params = re.findall(r'{(\w+)}', path)
        for param in uri_params:
            del kwargs[param]
            # locals()[param] = kwargs.get(param)
        return uri, uri_params, kwargs

    # 总方法 此方法不做参数合并支持范围更加广泛
    @staticmethod
    def request(path):

        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                # 此处的self是被装饰类的
                uri, _, kwargs = PyFeign.get_uri(path, **kwargs)
                url = self.root + uri

                return requests.request(url=url, **kwargs)

            return wrapper

        return decorator

    # get方法
    @staticmethod
    def get(path):
        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                # 此处的self是被装饰类的
                uri, uri_params, kwargs = PyFeign.get_uri(path, **kwargs)
                url = self.root + uri

                merge_params = PyFeign.merge_params(func, uri_params, **kwargs)

                return requests.get(url=url, **merge_params)

            return wrapper

        return decorator

    # post方法
    @staticmethod
    def post(path):
        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                # 此处的self是被装饰类的
                uri, uri_params, kwargs = PyFeign.get_uri(path, **kwargs)
                url = self.root + uri

                merge_params = PyFeign.merge_params(func, uri_params, **kwargs)

                return requests.post(url=url, **merge_params)

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
    def test_post(self, book: dict):
        pass

    @PyFeign.get("/getBookNum/{book_name}")
    def get_book_num(self, book_name):
        pass


if __name__ == '__main__':
    test = Test()

    response_request = test.test_request(method='GET')
    print(response_request.text)

    response_get = test.test_get()
    print(response_get.text)

    response_post = test.test_post(book={"book_name": "未来简史"})
    print(response_post.text)

    r = test.get_book_num(book_name="未来简史")
    print(json.loads(r.text))

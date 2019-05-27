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

    @staticmethod
    def request(path):

        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                # 此处的self是被装饰类的
                uri = path.format(**kwargs)
                params = re.findall(r'\{(\w+)\}', path)
                for param in params:
                    del kwargs[param]
                    # locals()[param] = kwargs.get(param)
                url = self.root + uri

                return requests.request(url=url, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def get(path):
        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                # 此处的self是被装饰类的
                uri = path.format(**kwargs)
                params = re.findall(r'\{(\w+)\}', path)
                for param in params:
                    del kwargs[param]

                url = self.root + uri
                return requests.get(url=url, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def post(path):
        def decorator(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                # 此处的self是被装饰类的
                uri = path.format(**kwargs)
                params = re.findall(r'\{(\w+)\}', path)
                for param in params:
                    del kwargs[param]

                url = self.root + uri
                return requests.post(url=url, **kwargs)

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


if __name__ == '__main__':
    import json

    test = Test()

    response_request = test.test_request(method='GET')
    print(response_request.text)
    response_get = test.test_get()
    print(response_get.text)
    response_post = test.test_post(data=json.dumps({"book_name": "未来简史"}))
    print(response_post.text)

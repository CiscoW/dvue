import os
import django

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'dvue.settings')
    django.setup()
    # 一定要在此处导入否则报错
    from myapp.views import test_log

    # synchronous_data(update_method="自动同步")
    for i in range(10000):
        test_log()
        print(i+1)

# linux中 crontab -e 设定每分钟一次执行
# */1 * * * * /usr/local/app/pyweb/bin/python /usr/local/app/autodeployment/timing_task.py
# service crond restart

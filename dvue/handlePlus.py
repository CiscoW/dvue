import time
import os
import shutil
import logging.handlers
from logging import Handler
from logging.handlers import BaseRotatingHandler
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from .filelock import lock
from .filelock import unlock


class RotatingFileHandlerPlus(RotatingFileHandler):

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" % (self.baseFilename,
                                                        i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)

            # 改成复制后 清空原文件
            shutil.copy(self.baseFilename, dfn)

        if not self.delay:
            self.stream = self._open()
            self.stream.truncate(0)


class TimedRotatingFileHandlerPlus(TimedRotatingFileHandler):

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        if os.path.exists(dfn):
            os.remove(dfn)

        # 复制原文件
        shutil.copy(self.baseFilename, dfn)

        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
            # 清空原文件
            self.stream.truncate(0)
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


# 重写Handler中的handle方法 实现文件锁，以用于多进程多线程都可用
def handle(self, record):
    rv = self.filter(record)
    if rv:
        f = open("lock.file", "a")
        lock(f)
        try:
            self.emit(record)
        finally:
            unlock(f)
            f.close()

    return rv


# handle上加锁有点晚 加载emit上会更好些
def emit(self, record):
    """
    Emit a record.

    Output the record to the file, catering for rollover as described
    in doRollover().
    """
    try:
        f = open("lock.file", "a")
        lock(f)
        if self.shouldRollover(record):
            self.doRollover()
        logging.FileHandler.emit(self, record)
    except Exception:
        self.handleError(record)

    finally:
        unlock(f)
        f.close()


# setattr(Handler, 'handle', handle)
setattr(BaseRotatingHandler, 'emit', emit)
logging.handlers.RotatingFileHandlerPlus = RotatingFileHandlerPlus
logging.handlers.TimedRotatingFileHandlerPlus = TimedRotatingFileHandlerPlus

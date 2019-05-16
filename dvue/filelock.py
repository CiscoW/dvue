try:
    import fcntl


    def lock(file):
        flags = fcntl.LOCK_EX  # | fcntl.LOCK_NB
        fcntl.flock(file, flags)


    def unlock(file):
        fcntl.flock(file, fcntl.LOCK_UN)

except ModuleNotFoundError:
    import win32con
    import win32file
    import pywintypes


    def lock(file):
        flags = win32con.LOCKFILE_EXCLUSIVE_LOCK  # | win32con.LOCKFILE_FAIL_IMMEDIATELY
        __overlapped = pywintypes.OVERLAPPED()
        h_file = win32file._get_osfhandle(file.fileno())
        win32file.LockFileEx(h_file, flags, 0, 0xffff0000, __overlapped)


    def unlock(file):
        __overlapped = pywintypes.OVERLAPPED()
        h_file = win32file._get_osfhandle(file.fileno())
        win32file.UnlockFileEx(h_file, 0, 0xffff0000, __overlapped)

if __name__ == '__main__':
    f = open("lock.file", "a")
    lock(f)
    unlock(f)

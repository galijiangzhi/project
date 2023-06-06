class _BaseException(Exception):
    """base异常，不可使用
    """

    def __init__(self, msg, code = "ERR-999"):
        self.code = code
        self.msg = msg

    def __str__(self):
        return ("%s:%s" % (self.code, self.msg))


class CriticalException(_BaseException):
    """系统异常，无法继续运转
    """


class ErrorException(_BaseException):
    """错误需要处理，系统还能继续运转。比如账户密码错误，或者人数和实际不匹配等
    """


class WarningException(_BaseException):
    """不是错误，只是一个警告，系统不需要做任何处理，还能继续运转。比如操作太频繁，只需要等一段时间就自动恢复
    """

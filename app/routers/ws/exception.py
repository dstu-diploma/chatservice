from fastapi import WebSocketException, status


class NoActionProvidenException(WebSocketException):
    def __init__(self):
        super().__init__(code=status.WS_1003_UNSUPPORTED_DATA)


class NoAuthTokenProvidenException(WebSocketException):
    def __init__(self):
        super().__init__(code=status.WS_1003_UNSUPPORTED_DATA)

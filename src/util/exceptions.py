class HTTPException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.message)


class ServerException(HTTPException):
    def __init__(self, message):
        super(ServerException, self).__init__(500, message)


class UserException(HTTPException):
    def __init__(self, message):
        super(UserException, self).__init__(400, message)


class NotFoundException(HTTPException):
    def __init__(self, message):
        super(NotFoundException, self).__init__(404, message)


class NotImplementedException(HTTPException):
    def __init__(self):
        super(NotImplementedException, self).__init__(501, 'NYI')


class ModelValidationException(Exception):
    pass

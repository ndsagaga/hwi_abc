class AuthError(Exception):
    code = 401
    message = "Authentication failed."

    def __init__(self, message):
        self.message = message

class ForbiddenError(Exception):
    code = 403
    message = "User does not have enough privilege."

    def __init__(self, message):
        self.message = message

class BadRequestError(Exception):
    code = 400
    message = "Request has missing values."

    def __init__(self, message):
        self.message = message

class InternalError(Exception):
    code = 500
    message = "Something went wrong."

    def __init__(self, message):
        self.message = message
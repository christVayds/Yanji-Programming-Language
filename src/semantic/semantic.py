
class Warning:
    
    def __init__(self, msg):
        self.msg = msg

class Error:

    def __init__(self, msg, token):
        self.msg = msg
        self.token = token

class SyntaxError(Error):

    def __init__(self, msg, token):
        super.__init__(msg, token)


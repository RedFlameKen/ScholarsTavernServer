import json


class Checker():
    def __init__(self, success=False, status=200, message="", data={}):
        self.success = success
        self.status = status
        self.message = message
        self.data = data

    def __str__(self):
        return json.dumps(self.__dict__)

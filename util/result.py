import json


class Result():
    def __init__(self, error=None, data=None, status=200):
        self.status = status
        self.error = error
        self.data = data

    def isOk(self):
        return self.error is None

    def __str__(self):
        return json.dumps(self.__dict__)

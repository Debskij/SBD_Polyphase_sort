class FifthRecordType(object):
    def __init__(self, value: str):
        if value:
            self.value = value
        else:
            raise ValueError

    def __call__(self, *args, **kwargs):
        return self.value

    def __lt__(self, other):
        if type(other) == FifthRecordType:
            return self.value < other.value
        if type(other) == int:
            return ord(list(self.value)[0]) < other

    def __le__(self, other):
        if type(other) == FifthRecordType:
            return self.value <= other.value
        if type(other) == int:
            return ord(list(self.value)[0]) <= other

    def __eq__(self, other):
        if type(other) == FifthRecordType:
            return self.value == other.value
        if type(other) == int:
            return ord(list(self.value)[0]) == other

    def __ne__(self, other):
        if type(other) == FifthRecordType:
            return self.value != other.value
        if type(other) == int:
            return ord(list(self.value)[0]) != other

    def __gt__(self, other):
        if type(other) == FifthRecordType:
            return self.value > other.value
        if type(other) == int:
            return ord(list(self.value)[0]) > other

    def __ge__(self, other):
        if type(other) == FifthRecordType:
            return self.value >= other.value
        if type(other) == int:
            return ord(list(self.value)[0]) >= other

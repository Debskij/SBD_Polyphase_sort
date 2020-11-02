class FifthRecordType(object):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def max(list_of_ascii: list):
        try:
            return max(list_of_ascii)
        except ValueError:
            return 0

    def form_sets(self, other):
        return set(self.value).difference(set(other.value)), set(other.value).difference(set(self.value))

    def __lt__(self, other):
        set_this, set_other = self.form_sets(other)
        return self.max([ord(c) for c in set_this] + 0) < self.max([ord(c) for c in set_other])

    def __le__(self, other):
        set_this, set_other = self.form_sets(other)
        return self.max([ord(c) for c in set_this]) <= self.max([ord(c) for c in set_other])

    def __eq__(self, other):
        set_this, set_other = self.form_sets(other)
        return self.max([ord(c) for c in set_this]) == self.max([ord(c) for c in set_other])

    def __ne__(self, other):
        set_this, set_other = self.form_sets(other)
        return self.max([ord(c) for c in set_this]) != self.max([ord(c) for c in set_other])

    def __gt__(self, other):
        set_this, set_other = self.form_sets(other)
        return self.max([ord(c) for c in set_this]) > self.max([ord(c) for c in set_other])

    def __ge__(self, other):
        set_this, set_other = self.form_sets(other)
        return self.max([ord(c) for c in set_this]) >= self.max([ord(c) for c in set_other])
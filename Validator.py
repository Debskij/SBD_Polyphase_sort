class Validator:
    def validate(self, path):
        with open(path, 'r+') as file:
            for line in file.readlines():
                print(max([ord(c) for c in line]))


v = Validator()
v.validate('test.txt')

import os


class Validator:
    @staticmethod
    def validate(paths: list):
        path = max([(path_name, os.path.getsize(path_name)) for path_name in paths], key=lambda x: x[1])[0]
        with open(path, 'r+') as file:
            d = file.readlines()
            return d == sorted(d)

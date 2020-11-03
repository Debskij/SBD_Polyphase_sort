import string
import random


class Helpers:
    @staticmethod
    def copy_data(path_1, path_2):
        with open(path_1, 'r+') as src:
            with open(path_2, 'r+') as dst:
                d = src.readlines()
                for line in d:
                    dst.write(f'{line}')

    @staticmethod
    def generate(amount_of_records: int, max_length: int, file_path=None) -> list:
        chars = string.ascii_letters + string.digits
        # chars = string.digits
        records = [''.join((random.choice(chars) for _ in range(random.randint(1, max_length)))) for _ in
                   range(amount_of_records)]
        if file_path:
            with open(file_path, 'w') as f:
                for record in records[:-1]:
                    f.write(f'{record}\n')
                f.write(f'{records[-1]}')
        else:
            return records

    @staticmethod
    def erase_files(file_path: list):
        for file in file_path:
            with open(file, 'r+') as f:
                f.truncate()

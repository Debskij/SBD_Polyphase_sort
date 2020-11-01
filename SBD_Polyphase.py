import string
import typing
import math
import random
import mmap


def generate(amount_of_records: int, max_length: int, file_path=None) -> list:
    # chars = string.ascii_letters + string.digits
    chars = string.digits
    records = [''.join((random.choice(chars) for _ in range(random.randint(1, max_length)))) for _ in
               range(amount_of_records)]
    if file_path:
        with open(file_path, 'w') as f:
            for record in records[:-1]:
                f.write(f'{record}\n')
            f.write(f'{records[-1]}')
    else:
        return records


class DatabaseAccessor:
    def __init__(self, first_tape: str, second_tape: str, third_tape: str):
        self.tapes = (open(first_tape, 'r+'), open(second_tape, 'r+'), open(third_tape, 'r+'))
        self.data_base_accesses = [0, 0]

    def read_from_tape(self, tape_no: int):
        try:
            record = self.tapes[tape_no].readline().strip('\n')
            self.data_base_accesses[0] += 1
            self.delete_from_tape(tape_no)
            return int(record)
        except:
            print("ERROR WHILE READING")
            return None

    def delete_from_tape(self, tape_no: int):
        d = self.tapes[tape_no].readlines()
        self.tapes[tape_no].seek(0)
        self.tapes[tape_no].truncate()
        for i in range(0, len(d)):
            self.tapes[tape_no].write(d[i])
        self.tapes[tape_no].seek(0)

    def save_to_tape(self, tape_no: int, value):
        try:
            self.tapes[tape_no].write(f'{str(value)}\n')
            self.tapes[tape_no].flush()
            self.data_base_accesses[1] += 1
            return True
        except:
            print("ERROR WHILE SAVING")
            return False

    def read_write_status(self):
        return f'read operations: {self.data_base_accesses[0]}, write operations: {self.data_base_accesses[1]}'


class Sorter:
    def __init__(self, buffer_size: int, database: DatabaseAccessor):
        self.buffer_size = buffer_size
        self.buffer = list()
        self.db = database
        self.dummy_runs = 0

    def initial_phase(self):
        fib = [1, 0]
        input_tape = 0
        output_tape = [1, 2]
        self.write_series(input_tape, output_tape[1])
        idx = 0
        try:
            while True:
                while idx < fib[0]:
                    idx += 1
                    self.write_series(input_tape, output_tape[0])
                    print(f'end of serie {idx}')
                output_tape[0], output_tape[1] = output_tape[1], output_tape[0]
                fib = fib[0]+fib[1], fib[0]
                idx = 0
                print(fib)
        except IndexError as e:
            print(idx)
            self.dummy_runs = fib[0] - idx if idx else 0
            print(self.dummy_runs)

    def write_series(self, input_tape: int, output_tape: int):
        previous = None
        while True:
            if len(self.buffer):
                data.save_to_tape(output_tape, self.buffer[0])
                previous = self.buffer[0]
                del self.buffer[0]
            record = data.read_from_tape(input_tape)
            print(f'previous: {previous}, actual: {record}, tape no: {output_tape}')
            if record:
                self.buffer.append(record)
                if previous and previous > record:
                    data.save_to_tape(output_tape, '')
                    return True
                else:
                    data.save_to_tape(output_tape, self.buffer[0])
                    previous = self.buffer[0]
                    del self.buffer[0]
            else:
                raise IndexError


generate(20, 10, 'test.txt')

data = DatabaseAccessor('test.txt', 'tape2.txt', 'tape3.txt')
sort = Sorter(10, data)
sort.initial_phase()
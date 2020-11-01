import string
import random
from sys import maxsize

DEBUG_VARIABLES = {'database_log': False, 'distribution_log': False}


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


def erase_files(file_path: list):
    for file in file_path:
        with open(file, 'r+') as f:
            f.truncate()


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
            if DEBUG_VARIABLES['database_log']:
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
            if DEBUG_VARIABLES['database_log']:
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
        output_tape = [2, 1]
        last_record = [maxsize * 2 + 1, maxsize * 2 + 1]
        last_record[0], length_of_serie = self.write_series(input_tape, 1)
        idx = 0
        while length_of_serie:
            idx = 0
            self.coaelescented_series(input_tape, output_tape[0], last_record[output_tape[0]-1])
            while idx < fib[0] and length_of_serie:
                temp, length_of_serie = self.write_series(input_tape, output_tape[0])
                if length_of_serie:
                    last_record[output_tape[0]-1] = temp
                    idx += 1
                if DEBUG_VARIABLES['distribution_log']:
                    print(f'end of serie {idx}')
            output_tape[0], output_tape[1] = output_tape[1], output_tape[0]
            fib = fib[0] + fib[1], fib[0]
            if DEBUG_VARIABLES['distribution_log']:
                print(f'last records {last_record}')
        self.dummy_runs = fib[1] - idx if idx else 0
        if DEBUG_VARIABLES['distribution_log']:
            print(f'Dummy runs count: {self.dummy_runs}')

    def coaelescented_series(self, input_tape: int, output_tape: int, last_value_from_previous):
        if len(self.buffer) and self.buffer[0] > last_value_from_previous:
            if DEBUG_VARIABLES['distribution_log']:
                print(f'FOUND COALESCENTED SERIES! PREVIOUS VALUE {last_value_from_previous}')
            return self.write_series(input_tape, output_tape)

    def write_series(self, input_tape: int, output_tape: int):
        previous = None
        last_assigned_value = None
        length_of_serie = 0
        while True:
            if len(self.buffer):
                data.save_to_tape(output_tape, self.buffer[0])
                if DEBUG_VARIABLES['distribution_log']:
                    print(f'value {self.buffer[0]} written to serie on tape {output_tape}')
                length_of_serie += 1
                last_assigned_value = previous
                previous = self.buffer[0]
                del self.buffer[0]
            record = data.read_from_tape(input_tape)
            if record:
                self.buffer.append(record)
                if previous and previous > record:
                    last_assigned_value = previous
                    data.save_to_tape(output_tape, '')
                    return last_assigned_value, length_of_serie
                else:
                    data.save_to_tape(output_tape, self.buffer[0])
                    if DEBUG_VARIABLES['distribution_log']:
                        print(f'value {self.buffer[0]} written to serie on tape {output_tape}')
                    length_of_serie += 1
                    last_assigned_value = previous
                    previous = self.buffer[0]
                    del self.buffer[0]
            else:
                return last_assigned_value, length_of_serie


generate(20, 10, 'test.txt')
erase_files(['tape2.txt', 'tape3.txt'])
data = DatabaseAccessor('test.txt', 'tape2.txt', 'tape3.txt')
sort = Sorter(10, data)
sort.initial_phase()

import string
import random
from sys import maxsize

DEBUG_VARIABLES = {'database_log': False,
                   'distribution_log': False,
                   'merge_log': True}


def copy_data(path_1, path_2):
    with open(path_1, 'r+') as src:
        with open(path_2, 'r+') as dst:
            d = src.readlines()
            for line in d:
                dst.write(f'{line}')


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


class Logger:
    def __init__(self):
        self.log = []
        self.dbg_variables = {'database_log': True,
                              'distribution_log': False,
                              'merge_log': False}

    def __call__(self, *args, **kwargs):
        try:
            if self.dbg_variables[args[0]]:
                self.log.append(args[1])
        except:
            pass

    def save_log_to_file(self, path):
        try:
            with open(path, 'r+') as file:
                for line in self.log:
                    file.write(line)
        except:
            pass

    def print_log(self):
        for line in self.log:
            print(line)


class DatabaseAccessor:
    def __init__(self, first_tape: str, second_tape: str, third_tape: str):
        self.paths = (first_tape, second_tape, third_tape)
        self.tapes = (open(first_tape, 'r+'), open(second_tape, 'r+'), open(third_tape, 'r+'))
        self.data_base_accesses = [0, 0]

    def read_from_tape(self, tape_no: int):
        try:
            record = self.tapes[tape_no].readline().strip('\n')
            log('database_log', f'Read from tape {tape_no} value {record}')
            self.data_base_accesses[0] += 1
            self.delete_from_tape(tape_no)
            return int(record)
        except (ValueError, IOError):
            log('database_log', "ERROR WHILE READING")
            return None

    def flush_whole_db(self):
        for tape in self.tapes:
            tape.close()
        self.tapes = (open(self.paths[0], 'r+'), open(self.paths[1], 'r+'), open(self.paths[2], 'r+'))

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
        except(ValueError, IOError):
            log('database_log', "ERROR WHILE SAVING")
            return False

    def read_write_status(self):
        return f'read operations: {self.data_base_accesses[0]}, write operations: {self.data_base_accesses[1]}'


class Sorter:
    def __init__(self, buffer_size: int, database: DatabaseAccessor):
        self.buffer_size = buffer_size
        self.buffer = list()
        self.db = database
        self.dummy_runs = 0
        self.tapes_sequence = []
        self.expected_number_of_merges = 0

    def initial_distribution(self):
        fib = [1, 0]
        input_tape = 0
        output_tape = [2, 1]
        last_record = [maxsize * 2 + 1, maxsize * 2 + 1]
        tapes_series = [1, 0]
        last_record[0], length_of_serie = self.initial_distribution_write_series(input_tape, 1)
        idx = 0
        while length_of_serie:
            idx = 0
            self.coalescence_series(input_tape, output_tape[0], last_record[output_tape[0] - 1])
            while idx < fib[0] and length_of_serie:
                temp, length_of_serie = self.initial_distribution_write_series(input_tape, output_tape[0])
                if length_of_serie:
                    tapes_series[output_tape[0] - 1] += 1
                    last_record[output_tape[0] - 1] = temp
                    idx += 1
                log('distribution_log', f'end of serie {idx}')
            output_tape[0], output_tape[1] = output_tape[1], output_tape[0]
            self.expected_number_of_merges += 1
            fib = fib[0] + fib[1], fib[0]
            log('distribution_log', f'last records {last_record}')
        self.dummy_runs = fib[1] - idx if idx else 0
        log('distribution_log', f'Output tape: {output_tape}')
        print(f'Amount of series on tapes: {tapes_series}')
        print(f'Dummy runs count: {self.dummy_runs}')
        return [output_tape[1], output_tape[0]]  # Which tape yields dummy runs

    def coalescence_series(self, input_tape: int, output_tape: int, last_value_from_previous):
        if len(self.buffer) and self.buffer[0] > last_value_from_previous:
            log('distribution_log', f'FOUND COALESCENTED SERIES! PREVIOUS VALUE {last_value_from_previous}')
            return self.initial_distribution_write_series(input_tape, output_tape)

    def initial_distribution_write_series(self, input_tape: int, output_tape: int):
        previous = None
        last_assigned_value = None
        length_of_serie = 0
        while True:
            if len(self.buffer):
                self.db.save_to_tape(output_tape, self.buffer[0])
                log('distribution_log', f'value {self.buffer[0]} written to serie on tape {output_tape}')
                length_of_serie += 1
                last_assigned_value = previous
                previous = self.buffer[0]
                del self.buffer[0]
            record = self.db.read_from_tape(input_tape)
            if record:
                self.buffer.append(record)
                if previous and previous > record:
                    last_assigned_value = previous
                    return last_assigned_value, length_of_serie
                else:
                    self.db.save_to_tape(output_tape, self.buffer[0])
                    log('distribution_log', f'value {self.buffer[0]} written to serie on tape {output_tape}')
                    length_of_serie += 1
                    last_assigned_value = previous
                    previous = self.buffer[0]
                    del self.buffer[0]
            else:
                return last_assigned_value, length_of_serie

    def rotate_sequence(self):
        self.tapes_sequence = self.tapes_sequence[-1:] + self.tapes_sequence[:-1]

    def merge_dummy_runs(self):
        previous_value = [0, 0]
        while self.dummy_runs:
            self.refill_buffer()
            log('merge_log', f'buffer dummy_runs: {self.buffer}')
            if previous_value[1] > self.buffer[1]:
                self.dummy_runs -= 1
                log('merge_log', f'One series ended. {self.dummy_runs} left')
                if not self.dummy_runs:
                    break
            self.db.save_to_tape(self.tapes_sequence[2], self.buffer[1])
            log('merge_log', f'Saved value {self.buffer[1]}')
            previous_value[1] = self.buffer[1]
            self.buffer[1] = None
        log('merge_log', f'Buffer after: {self.buffer}')

    def merge_two_tapes(self):
        previous_values = [0, 0]
        which_serie = [0, 0]

        while None not in self.buffer:
            self.refill_buffer()
            log('merge_log', f'Buffer: {self.buffer}\nPrevious values: {previous_values}')
            if previous_values[0] > self.buffer[0]:
                while None not in self.buffer and previous_values[1] < self.buffer[1]:
                    self.db.save_to_tape(self.tapes_sequence[2], self.buffer[1])
                    previous_values[1] = self.buffer[1]
                    self.buffer[1] = None
                    self.refill_buffer()
                previous_values[0] = self.buffer[0]
                which_serie[0] += 1
                continue
            elif previous_values[1] > self.buffer[1]:
                while None not in self.buffer and previous_values[0] < self.buffer[0]:
                    self.db.save_to_tape(self.tapes_sequence[2], self.buffer[0])
                    previous_values[0] = self.buffer[0]
                    self.buffer[0] = None
                    self.refill_buffer()
                previous_values[1] = self.buffer[1]
                which_serie[1] += 1
                continue
            elif self.buffer[0] < self.buffer[1]:
                self.db.save_to_tape(self.tapes_sequence[2], self.buffer[0])
                previous_values[0] = self.buffer[0]
                self.buffer[0] = None
                self.refill_buffer()
            else:
                self.db.save_to_tape(self.tapes_sequence[2], self.buffer[1])
                previous_values[1] = self.buffer[1]
                self.buffer[1] = None
                self.refill_buffer()
        print(which_serie)
        self.buffer = [self.buffer[1], self.buffer[0]]

    def merge_phase(self):
        self.merge_dummy_runs()
        for _ in range(self.expected_number_of_merges + 4):
            log('merge_log', f'tapes sequence: {self.tapes_sequence}')
            log('merge_log', f'buffer: {self.buffer}')
            self.merge_two_tapes()
            self.db.flush_whole_db()
            self.rotate_sequence()
            self.refill_buffer()
            log('merge_log', f'tapes sequence: {self.tapes_sequence}')
            log('merge_log', f'buffer tape {self.tapes_sequence[0]}: {self.buffer[0]}')
            log('merge_log', f'buffer tape {self.tapes_sequence[1]}: {self.buffer[1]}')

    def entry_point(self):
        self.tapes_sequence = [*self.initial_distribution(), 0]
        self.db.flush_whole_db()
        self.buffer = [None, None]
        log('merge_log', f'tapes sequence: {self.tapes_sequence}')
        log('merge_log', f'expected merges amount: {self.expected_number_of_merges}')
        self.merge_phase()

    def refill_buffer(self):
        self.buffer = [self.db.read_from_tape(self.tapes_sequence[0]) if not self.buffer[0] else self.buffer[0],
                       self.db.read_from_tape(self.tapes_sequence[1]) if not self.buffer[1] else self.buffer[1]]
        return None not in self.buffer


log = Logger()

erase_files(['test.txt', 'tape2.txt', 'tape3.txt'])
# generate(30, 6, 'basic_test')
copy_data('basic_test', 'test.txt')
data = DatabaseAccessor('test.txt', 'tape2.txt', 'tape3.txt')
sort = Sorter(10, data)
sort.entry_point()
log.print_log()
# print(data.read_write_status())

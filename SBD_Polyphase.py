from sys import maxsize

from DatabaseAccessor import DatabaseAccessor
from Logger import Logger
from Helpers import Helpers
from FifthRecordType import FifthRecordType
from Validator import Validator


class Sorter:
    def __init__(self, database: DatabaseAccessor, log: Logger):
        self.buffer = list()
        self.db = database
        self.log = log
        self.dummy_runs = 0
        self.tapes_sequence = []

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
            self.log('distribution_log', f'trying to put {fib[0]} series into tape {output_tape[0]}')
            while idx < fib[0] and length_of_serie:
                temp, length_of_serie = self.initial_distribution_write_series(input_tape, output_tape[0])
                if length_of_serie:
                    tapes_series[output_tape[0] - 1] += 1
                    last_record[output_tape[0] - 1] = temp
                    idx += 1
                self.log('distribution_log', f'end of serie {idx}')
            output_tape[0], output_tape[1] = output_tape[1], output_tape[0]
            fib = fib[0] + fib[1], fib[0]
            self.log('distribution_log', f'last records {self.print_fifth_type(last_record)}')
        self.dummy_runs = fib[1] - idx if idx else 0
        self.log('distribution_log', f'Output tape: {output_tape}')
        self.log('distribution_log', f'Amount of series on tapes: {tapes_series}')
        self.log('distribution_log', f'Dummy runs count: {self.dummy_runs}')
        return output_tape[::-1] if idx else output_tape  # Which tape yields dummy runs

    def coalescence_series(self, input_tape: int, output_tape: int, last_value_from_previous):
        if len(self.buffer) and self.buffer[0] > last_value_from_previous:
            self.log('distribution_log',
                     f'FOUND COALESCENTED SERIES! PREVIOUS VALUE '
                     f'{last_value_from_previous.__call__()}')
            return self.initial_distribution_write_series(input_tape, output_tape)

    def initial_distribution_write_series(self, input_tape: int, output_tape: int):
        previous = None
        last_assigned_value = None
        length_of_serie = 0
        while True:
            if len(self.buffer):
                self.db.save_to_tape(output_tape, self.buffer[0])
                self.log('distribution_log', f'value {self.print_buffer()[0]} written to serie on tape {output_tape}')
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
                    self.log('distribution_log',
                             f'value {self.print_buffer()[0]} written to serie on tape {output_tape}')
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
        self.buffer[1] = self.db.read_from_tape(self.tapes_sequence[1])
        while self.dummy_runs:
            self.log('merge_log', f'buffer dummy_runs: {self.print_buffer()}')
            if previous_value[1] > self.buffer[1]:
                self.dummy_runs -= 1
                self.log('merge_log', f'One series ended. {self.dummy_runs} left')
                if not self.dummy_runs:
                    break
            self.db.save_to_tape(self.tapes_sequence[2], self.buffer[1])
            self.log('merge_log', f'Saved value {self.print_buffer()[1]}')
            previous_value[1] = self.buffer[1]
            self.buffer[1] = self.db.read_from_tape(self.tapes_sequence[1])
        self.log('merge_log', f'Buffer after: {self.print_buffer()}')

    def print_buffer(self):
        return [x.__call__() if type(x) == FifthRecordType else x for x in self.buffer]

    def print_fifth_type(self, list_of_val: list):
        return [x.__call__() if type(x) == FifthRecordType else x for x in list_of_val]

    def merge_two_tapes(self):
        previous_values = [-1, -1]
        self.refill_buffer()
        while None not in self.buffer:
            runs = [False, False]
            self.log('merge_log', f'tapes sequence: {self.tapes_sequence}')
            self.log('merge_log', f'buffer: {self.print_buffer()}')
            if self.buffer[0] < self.buffer[1]:
                self.db.save_to_tape(self.tapes_sequence[2], self.buffer[0])
                previous_values[0] = self.buffer[0]
                self.buffer[0] = self.db.read_from_tape(self.tapes_sequence[0])
                if not self.buffer[0] or self.buffer[0] < previous_values[0]:
                    self.log('merge_log', f'end of run on tape {self.tapes_sequence[0]}\nactual value {self.buffer[0]}')
                    runs[0] = True
            else:
                self.db.save_to_tape(self.tapes_sequence[2], self.buffer[1])
                previous_values[1] = self.buffer[1]
                self.buffer[1] = self.db.read_from_tape(self.tapes_sequence[1])
                if not self.buffer[1] or self.buffer[1] < previous_values[1]:
                    self.log('merge_log', f'end of run on tape {self.tapes_sequence[1]}\nactual value {self.buffer[1]}')
                    runs[1] = True
            if runs[0]:
                self.merge_serie(1, previous_values[1])
                previous_values[1] = -1
                self.log('merge_log', f'end of run on tape {self.tapes_sequence[1]}\nactual value {self.buffer[1]}')
            elif runs[1]:
                self.merge_serie(0, previous_values[0])
                previous_values[0] = -1
                self.log('merge_log', f'end of run on tape {self.tapes_sequence[0]}\nactual value {self.buffer[0]}')

    def merge_serie(self, buffer_idx, last_value):
        while self.buffer[buffer_idx] and last_value < self.buffer[buffer_idx]:
            self.db.save_to_tape(self.tapes_sequence[2], self.buffer[buffer_idx])
            last_value = self.buffer[buffer_idx]
            self.buffer[buffer_idx] = self.db.read_from_tape(self.tapes_sequence[buffer_idx])
        return last_value

    def merge_phase(self):
        self.merge_dummy_runs()
        self.refill_buffer()
        while not all(v is None for v in self.buffer):
            self.merge_two_tapes()
            self.db.flush_whole_db()
            self.rotate_sequence()
            self.log('merge_log', f'tapes sequence: {self.tapes_sequence}')
            self.buffer[0], self.buffer[1] = self.buffer[1], self.buffer[0]
            self.log('merge_log', f'buffer tape {self.tapes_sequence[1]}: {self.print_buffer()[0]}')

    def entry_point(self):
        self.tapes_sequence = [*self.initial_distribution(), 0]
        self.db.flush_whole_db()
        self.buffer = [None, None]
        self.log('merge_log', f'tapes sequence: {self.tapes_sequence}')
        self.merge_phase()

    def refill_buffer(self):
        self.buffer = [self.db.read_from_tape(self.tapes_sequence[0]) if not self.buffer[0] else self.buffer[0],
                       self.db.read_from_tape(self.tapes_sequence[1]) if not self.buffer[1] else self.buffer[1]]
        return None not in self.buffer


log = Logger()

Helpers.erase_files(['tape0.txt', 'tape1.txt', 'tape2.txt'])
Helpers.generate(100, 30, 'basic_test_fifth')
Helpers.copy_data('basic_test_fifth', 'tape0.txt')
data = DatabaseAccessor('tape0.txt', 'tape1.txt', 'tape2.txt', log, 100)
sort = Sorter(data, log)
sort.entry_point()
log.print_log()
Validator.validate(['tape0.txt', 'tape1.txt', 'tape2.txt'])
print(data.read_write_status())

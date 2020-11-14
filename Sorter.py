import os
from sys import maxsize
from math import log2

from DatabaseAccessor import DatabaseAccessor
from Logger import Logger
from FifthRecordType import FifthRecordType


def print_fifth_type(list_of_val: list):
    return [x.__call__() if type(x) == FifthRecordType else x for x in list_of_val]


class Sorter:
    def __init__(self, database: DatabaseAccessor, log: Logger):
        self.buffer = [None, None]
        self.db = database
        self.log = log
        self.dummy_runs = 0
        self.tapes_sequence = []

    def initial_distribution(self):
        fib = [1, 0]
        input_tape = 0
        output_tape = [2, 1]
        last_record = [maxsize * 2 + 1, maxsize * 2 + 1]
        last_record[0], is_serie_not_empty = self.initial_distribution_write_series(input_tape, 1)
        idx = 0
        while is_serie_not_empty:
            idx = 0
            self.coalescence_series(input_tape, output_tape[0], last_record[output_tape[0] - 1])
            self.log('distribution_log', f'trying to put {fib[0]} series into tape {output_tape[0]}')
            while idx < fib[0] and is_serie_not_empty:
                prev_record, is_serie_not_empty = self.initial_distribution_write_series(input_tape, output_tape[0])
                if is_serie_not_empty:
                    last_record[output_tape[0] - 1] = prev_record
                    idx += 1
                self.log('distribution_log', f'end of serie {idx}')
            output_tape[0], output_tape[1] = output_tape[1], output_tape[0]
            fib = fib[0] + fib[1], fib[0]
            self.log('distribution_log', f'last records {print_fifth_type(last_record)}')
        self.dummy_runs = fib[1] - idx if idx else 0
        self.log('distribution_log', f'Output tape: {output_tape}')
        self.log('distribution_log', f'Dummy runs count: {self.dummy_runs}')
        return output_tape[::-1] if idx else output_tape

    def coalescence_series(self, input_tape: int, output_tape: int, last_value_from_previous):
        if len(self.buffer) and last_value_from_previous and self.buffer[0] >= last_value_from_previous:
            self.log('distribution_log',
                     f'FOUND COALESCENTED SERIES! PREVIOUS VALUE '
                     f'{last_value_from_previous.__call__()}')
            return self.initial_distribution_write_series(input_tape, output_tape)

    def initial_distribution_write_series(self, input_tape: int, output_tape: int):
        previous = None
        not_empty_series = False
        length_of_serie = 0
        while True:
            if len(self.buffer):
                self.db.save_to_tape(output_tape, self.buffer[0])
                self.log('distribution_log', f'value {self.print_buffer()[0]} written to serie on tape {output_tape}')
                length_of_serie = True
                not_empty_series = previous
                previous = self.buffer[0]
                del self.buffer[0]
            record = self.db.read_from_tape(input_tape)
            if record:
                self.buffer.append(record)
                if previous and previous > record:
                    not_empty_series = previous
                    return not_empty_series, length_of_serie
                else:
                    self.db.save_to_tape(output_tape, self.buffer[0])
                    self.log('distribution_log',
                             f'value {self.print_buffer()[0]} written to serie on tape {output_tape}')
                    length_of_serie = True
                    not_empty_series = previous
                    previous = self.buffer[0]
                    del self.buffer[0]
            else:
                return not_empty_series, length_of_serie

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
                    self.log('merge_log', f'end of run on tape {self.tapes_sequence[0]}'
                                          f'\nactual value {self.buffer[0]}')
                    runs[0] = True
            else:
                self.db.save_to_tape(self.tapes_sequence[2], self.buffer[1])
                previous_values[1] = self.buffer[1]
                self.buffer[1] = self.db.read_from_tape(self.tapes_sequence[1])
                if not self.buffer[1] or self.buffer[1] < previous_values[1]:
                    self.log('merge_log', f'end of run on tape {self.tapes_sequence[1]}\n'
                                          f'actual value {self.buffer[1]}')
                    runs[1] = True
            if runs[0]:
                self.merge_serie(1, previous_values[1])
                previous_values = [-1, -1]
                self.log('merge_log', f'end of run on tape {self.tapes_sequence[1]}\n'
                                      f'actual value {self.buffer[1]}')
            elif runs[1]:
                self.merge_serie(0, previous_values[0])
                previous_values = [-1, -1]
                self.log('merge_log', f'end of run on tape {self.tapes_sequence[0]}\n'
                                      f'actual value {self.buffer[0]}')

    def merge_serie(self, buffer_idx, last_value):
        while self.buffer[buffer_idx] and last_value <= self.buffer[buffer_idx]:
            self.db.save_to_tape(self.tapes_sequence[2], self.buffer[buffer_idx])
            last_value = self.buffer[buffer_idx]
            self.buffer[buffer_idx] = self.db.read_from_tape(self.tapes_sequence[buffer_idx])
        return last_value

    def print_tapes_after_phase(self, phase_name: str):
        self.log('phase_log', f'tapes status after {phase_name}')
        tapes_values = self.db.show_all_tapes()
        for tape_idx in range(len(tapes_values)):
            if self.buffer[1] and tape_idx == self.tapes_sequence[1]:
                self.log('phase_log', f'tape {tape_idx}: {[self.buffer[1].__call__()] + tapes_values[tape_idx]}')
            else:
                self.log('phase_log', f'tape {tape_idx}: {tapes_values[tape_idx]}')

    def merge_phase(self):
        self.merge_dummy_runs()
        self.refill_buffer()
        phase_number = 0
        while not all(v is None for v in self.buffer):
            phase_number += 1
            self.merge_two_tapes()
            self.db.save_stuff_left_on_buffer(self.tapes_sequence[2])
            self.db.delete_from_tape(self.tapes_sequence[0])
            self.db.delete_from_tape(self.tapes_sequence[1])
            self.db.flush_whole_db()
            self.rotate_sequence()
            self.log('merge_log', f'tapes sequence: {self.tapes_sequence}')
            self.buffer[0], self.buffer[1] = self.buffer[1], self.buffer[0]
            self.print_tapes_after_phase(f'merge phase {phase_number}')
            self.log('merge_log', f'buffer tape {self.tapes_sequence[1]}: {self.print_buffer()[0]}')
        return phase_number

    def entry_point(self):
        self.tapes_sequence = [*self.initial_distribution(), 0]
        self.db.delete_from_tape(0)
        self.db.save_stuff_left_on_buffer(self.tapes_sequence[0])
        self.db.save_stuff_left_on_buffer(self.tapes_sequence[1])
        self.db.flush_whole_db()
        self.buffer = [None, None]
        self.log('merge_log', f'tapes sequence: {self.tapes_sequence}')
        phase_count = self.merge_phase()
        self.nerd_log(phase_count)
        return phase_count

    def nerd_log(self, phase_count):
        real_n = max(len([x for x in tape if x]) for tape in self.db.show_all_tapes())
        file_size = max([os.path.getsize(path_name) for path_name in self.db.paths])
        avg_record_size = file_size/real_n
        blocking_factor = self.db.block_size/avg_record_size
        self.log('nerd_log', f'theoretical number of phases: {1.45*log2(real_n/2)}')
        self.log('nerd_log', f'actual number of phases: {phase_count}')
        self.log('nerd_log', f'theoretical number of reads and writes: '
                             f'{2 * real_n * (1.04 * log2(real_n) - 0.04) / blocking_factor}')
        self.log('nerd_log', f'actual number of reads and writes: {self.db.show_sum_of_reads_and_writes()}')


    def refill_buffer(self):
        self.buffer = [self.db.read_from_tape(self.tapes_sequence[0]) if not self.buffer[0] else self.buffer[0],
                       self.db.read_from_tape(self.tapes_sequence[1]) if not self.buffer[1] else self.buffer[1]]
        return None not in self.buffer

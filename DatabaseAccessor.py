import Logger
from FifthRecordType import FifthRecordType

class DatabaseAccessor:
    def __init__(self, first_tape: str, second_tape: str, third_tape: str, log: Logger):
        self.paths = (first_tape, second_tape, third_tape)
        self.tapes = (open(first_tape, 'r+'), open(second_tape, 'r+'), open(third_tape, 'r+'))
        self.data_base_accesses = [0, 0]
        self.log = log

    def read_from_tape(self, tape_no: int):
        try:
            record = self.tapes[tape_no].readline().strip('\n')
            self.log('database_log', f'Read from tape {tape_no} value {record}')
            self.data_base_accesses[0] += 1
            self.delete_from_tape(tape_no)
            return FifthRecordType(record)
        except (ValueError, IOError):
            self.log('database_log', "ERROR WHILE READING")
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
            self.tapes[tape_no].write(f'{str(value.value)}\n')
            self.tapes[tape_no].flush()
            self.data_base_accesses[1] += 1
            self.log('database_log', f'Written value: {value.__call__()} to tape {tape_no}')
            return True
        except(ValueError, IOError):
            self.log('database_log', "ERROR WHILE SAVING")
            return False

    def read_write_status(self):
        return f'read operations: {self.data_base_accesses[0]}, write operations: {self.data_base_accesses[1]}'

import Logger
from FifthRecordType import FifthRecordType


class DatabaseAccessor:
    def __init__(self, first_tape: str, second_tape: str, third_tape: str, log: Logger, block_size: int, separator='\n'):
        self.paths = (first_tape, second_tape, third_tape)
        self.tapes = (open(first_tape, 'r+'), open(second_tape, 'r+'), open(third_tape, 'r+'))
        self.data_base_accesses = [0, 0]
        self.block_size = block_size
        self.tape_buffers = [''] * 3
        self.log = log
        self.separator = separator

    def read_from_tape(self, tape_no: int):
        temp_record = ''
        while True:
            if not len(self.tape_buffers[tape_no]):
                self.data_base_accesses[0] += 1
                self.tape_buffers[tape_no] = self.tapes[tape_no].read(self.block_size)
                self.delete_from_tape(tape_no)
            buffer_splitted = self.tape_buffers[tape_no].split(self.separator)
            if len(buffer_splitted) == 1 and len(buffer_splitted[0]):
                temp_record += buffer_splitted[0]
                self.data_base_accesses[0] += 1
                self.tape_buffers[tape_no] = self.tapes[tape_no].read(self.block_size)
                self.delete_from_tape(tape_no)
                if not self.tape_buffers[tape_no]:
                    return FifthRecordType(temp_record)
            if len(buffer_splitted) == 1 and not len(buffer_splitted[0]):
                return None
            if len(buffer_splitted) > 1:
                self.tape_buffers[tape_no] = self.separator.join(buffer_splitted[1:])
                if len(temp_record):
                    return FifthRecordType(str(temp_record + buffer_splitted[0]))
                else:
                    return FifthRecordType(buffer_splitted[0])

    def flush_whole_db(self):
        for tape in self.tapes:
            tape.close()
        self.tapes = (open(self.paths[0], 'r+'), open(self.paths[1], 'r+'), open(self.paths[2], 'r+'))

    def delete_from_tape(self, tape_no: int):
        d = self.tapes[tape_no].readlines()
        self.tapes[tape_no].seek(0)
        self.tapes[tape_no].truncate()
        self.tapes[tape_no].writelines(d)
        self.tapes[tape_no].seek(0)

    def save_to_tape(self, tape_no: int, value):
        if value:
            value = value.__call__() + self.separator
            if len(self.tape_buffers[tape_no]) + len(value) < self.block_size:
                self.tape_buffers[tape_no] += value
            elif len(self.tape_buffers[tape_no]) + len(value) >= self.block_size:
                free_space = self.block_size - len(self.tape_buffers[tape_no])
                self.tape_buffers[tape_no] += value[:free_space]
                while len(self.tape_buffers[tape_no]) == self.block_size:
                    self.data_base_accesses[1] += 1
                    self.tapes[tape_no].writelines(self.tape_buffers[tape_no])
                    value = value[free_space:]
                    free_space = self.block_size
                    self.tape_buffers[tape_no] = value[:free_space]

    def save_stuff_left_on_buffer(self, tape_no: int):
        self.data_base_accesses[1] += 1
        self.tapes[tape_no].writelines(self.tape_buffers[tape_no])
        self.tape_buffers[tape_no] = ''

    def read_write_status(self):
        return f'read operations: {self.data_base_accesses[0]}, write operations: {self.data_base_accesses[1]}'

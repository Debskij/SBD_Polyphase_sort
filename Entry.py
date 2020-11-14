from DatabaseAccessor import DatabaseAccessor
from Helpers import Helpers
from Logger import Logger
from Sorter import Sorter
from Validator import Validator


class Entry:
    def run_test(self, input_file: str,
                 log: Logger, block_size: int, measure_rw_from_db: bool):
        Helpers.copy_data(input_file, 'tape0.txt')
        data = DatabaseAccessor('tape0.txt', 'tape1.txt', 'tape2.txt', log, block_size)
        sort = Sorter(database=data, log=log)
        phase_count = sort.entry_point()
        log.print_log()
        if measure_rw_from_db:
            return data.show_sum_of_reads_and_writes(), phase_count
        else:
            return Validator.validate(['tape0.txt', 'tape1.txt', 'tape2.txt'])

    def test_run_once(self, max_record_length: int, amount_of_records: int,
                      file_to_generate: str, block_size: int, logger_config: dict,
                      measure_rw_from_db=False, **kwargs):
        log = Logger(dbg_variables=logger_config)
        Helpers.erase_files(['tape0.txt', 'tape1.txt', 'tape2.txt', file_to_generate])
        Helpers.generate(amount_of_records, max_record_length, file_to_generate)
        return self.run_test(input_file=file_to_generate,
                             log=log,
                             block_size=block_size,
                             measure_rw_from_db=measure_rw_from_db)

    def test_run_once_with_kb_input(self, max_record_length: int, file_to_generate: str,
                                    block_size: int, logger_config: dict, measure_rw_from_db=False,
                                    **kwargs):

        log = Logger(dbg_variables=logger_config)
        Helpers.erase_files(['tape0.txt', 'tape1.txt', 'tape2.txt', file_to_generate])
        if not self.insert_data(file_to_generate, max_record_length):
            return
        return self.run_test(input_file=file_to_generate,
                             log=log,
                             block_size=block_size,
                             measure_rw_from_db=measure_rw_from_db)

    def test_run_once_with_file_input(self, file_to_generate: str, block_size: int, logger_config: dict,
                                      measure_rw_from_db=False, **kwargs):
        log = Logger(dbg_variables=logger_config)
        Helpers.erase_files(['tape0.txt', 'tape1.txt', 'tape2.txt'])
        return self.run_test(input_file=file_to_generate,
                             log=log,
                             block_size=block_size,
                             measure_rw_from_db=measure_rw_from_db)

    def insert_data(self, file_to_generate: str, max_record_length: int):
        data = []
        print('Press q to exit')
        while True:
            input_v = input('Pass record value [a-zA-Z0-9]: ')
            if input_v == 'q':
                if str(input('Are you sure you want to exit? [y/n]\n'
                             'If no single character q will be added as record\t')) == 'y':
                    break
            while not input_v:
                input_v = input('Can\'t pass empty record!')
            while len(input_v) > max_record_length:
                input_v = input(f'Passed record is too long. Max length is {max_record_length}')
            data.append(str(input_v))
        with open(file_to_generate, 'r+') as f:
            for record in data[:-1]:
                f.write(f'{record}\n')
            f.write(str(data[-1]))
        if not len(data):
            print('Sorting empty list?')
            return False
        return True

    def test_run_multiple(self, max_record_length: int, amount_of_records: int,
                          file_to_generate: str, block_size: int,
                          logger_config: dict, amount_of_tests: int):
        passed = True
        while passed and amount_of_tests:
            amount_of_tests -= 1
            passed = self.test_run_once(max_record_length=max_record_length,
                                        amount_of_records=amount_of_records,
                                        file_to_generate=file_to_generate,
                                        block_size=block_size,
                                        logger_config=logger_config)
        if passed:
            print(f'Every test passed')
        else:
            print(f'{amount_of_tests} tests left. Last test data saved to {file_to_generate}')


class TextInterface:
    def __init__(self):
        self.current_status = ''
        self.entry_class = Entry()
        self.params = {
            'max_record_length': 30,
            'amount_of_records': 100,
            'block_size': 50,
            'amount_of_tests': 10,
            'file_to_generate': 'basic_test'
        }
        self.logger = {
            'database_log': False,
            'distribution_log': False,
            'merge_log': False,
            'phase_log': False,
            'nerd_log': False
        }
        self.callboard = {
            '1': self.entry_class.test_run_once,
            '2': self.entry_class.test_run_multiple,
            '3': self.entry_class.test_run_once_with_kb_input,
            '4': self.entry_class.test_run_once_with_file_input,
            '5': self.modify_test_params,
            '6': self.modify_logger_param
        }
        self.descriptions = [
            '1. run single random test with params',
            '2. run multiple random tests',
            '3. run single test with keyboard input',
            '4. run single test with delivered file input',
            '5. modify parameters',
            '6. modify logger info',
            '7. exit',
            'Operation: \t'
        ]

    def replace_floors(self, value):
        return value.replace('_', ' ')

    def modify_test_params(self, **kwargs):
        for key, val in self.params.items():
            while True:
                try:
                    tested_value = input(f'{self.replace_floors(key)}: ')
                    if type(val) == int:
                        self.params[key] = int(tested_value)
                        break
                    elif type(val) == str:
                        self.params[key] = str(tested_value)
                        break
                    raise ValueError
                except ValueError:
                    print('Invalid type. Try again.')
        return True

    def modify_logger_param(self, **kwargs):
        print('Boolean values supported only! Press 0 for False and 1 for True')
        for key, val in self.logger.items():
            while True:
                try:
                    tested_value = input(f'{self.replace_floors(key)}:')
                    if type(val) == bool:
                        self.logger[key] = bool(int(tested_value))
                        break
                    raise ValueError
                except ValueError:
                    print('Invalid type. Try again.')
        return True

    def runner(self):
        while True:
            print('\n'.join([f'{self.replace_floors(key)}: {val}' for key, val in self.logger.items()]))
            print('\n'.join([f'{self.replace_floors(key)}: {val}' for key, val in self.params.items()]))
            operator = input('\n' + '\n'.join(self.descriptions))
            while not '1' <= operator <= '7':
                operator = input('invalid option selected!\nOperation: \t')
            if operator == '7':
                break
            else:
                self.callboard[str(operator)].__call__(**{**self.params, 'logger_config': self.logger})


t = TextInterface()
t.runner()

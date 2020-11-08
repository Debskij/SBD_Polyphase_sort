from DatabaseAccessor import DatabaseAccessor
from Helpers import Helpers
from Logger import Logger
from Sorter import Sorter
from Validator import Validator


class Entry:
    def test_run_once(self, max_record_length: int, amount_of_records: int,
                      file_to_generate: str, block_size: int):
        log = Logger()
        Helpers.erase_files(['tape0.txt', 'tape1.txt', 'tape2.txt'])
        Helpers.generate(amount_of_records, max_record_length, file_to_generate)
        Helpers.copy_data(file_to_generate, 'tape0.txt')
        data = DatabaseAccessor('tape0.txt', 'tape1.txt', 'tape2.txt', log, block_size)
        sort = Sorter(data, log)
        sort.entry_point()
        log.print_log()
        return Validator.validate(['tape0.txt', 'tape1.txt', 'tape2.txt'])

    def test_run_multiple(self, max_record_length: int, amount_of_records: int,
                          file_to_generate: str, block_size: int,
                          amount_of_tests: int):
        passed = True
        while passed and amount_of_tests:
            amount_of_tests -= 1
            passed = self.test_run_once(max_record_length=max_record_length,
                                        amount_of_records=amount_of_records,
                                        file_to_generate=file_to_generate,
                                        block_size=block_size)
        if passed:
            print(f'Every test passed')
        else:
            print(f'{amount_of_tests} tests left. Last test data saved to {file_to_generate}')


e = Entry()
e.test_run_multiple(30, 20, 'basic_test', 20, 100)

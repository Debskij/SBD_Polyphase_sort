import math
import os

import matplotlib.pyplot as plt

from Entry import Entry


def give_avg_rec_size(path, number_of_records):
    return os.path.getsize(path) / number_of_records

block_sizes = [200]
max_record_size = 30
record_samples = [10 * x for x in range(2, 100)]
amount_of_phases_theoretical = [1.45*math.log2(x/2) for x in record_samples]
e = Entry()
for block_size in block_sizes:
    amount_of_rw_for_algorithm = []
    amount_of_rw_theoretical = []
    amount_of_phases_for_algorithm = []
    for amount_of_records in record_samples:
        rw, phases = e.test_run_once(max_record_length=max_record_size,
                                     amount_of_records=amount_of_records,
                                     block_size=block_size,
                                     file_to_generate='basic_test_fifth',
                                     measure_rw_from_db=True,
                                     logger_config={
                                         'database_log': False,
                                         'distribution_log': False,
                                         'merge_log': False,
                                         'phase_log': False,
                                         'nerd_log': False
                                     })
        amount_of_rw_for_algorithm.append(rw)
        amount_of_phases_for_algorithm.append(phases)
        blocking_factor = block_size / give_avg_rec_size('basic_test_fifth', amount_of_records)
        amount_of_rw_theoretical.append(
            2 * amount_of_records * (1.04 * math.log2(amount_of_records) - 0.04) / blocking_factor)
    plt.plot(record_samples, amount_of_rw_theoretical)
    plt.plot(record_samples, amount_of_rw_for_algorithm)
    plt.title(f'Ilosc odczytow i zapisów dla rozmiaru bloku {block_size}')
    plt.xlabel('ilość rekordów')
    plt.ylabel('ilość read/write')
    plt.legend(['teoretyczna ilość read/write', 'ilość read/write wykonywana przez algorytm'])
    plt.savefig(f'read_write_{block_size}.png', dpi=300)
    plt.close()
plt.plot(record_samples, amount_of_phases_theoretical)
plt.plot(record_samples, amount_of_phases_for_algorithm)
plt.title('Ilosc faz w zależności od ilości rekordów')
plt.xlabel('ilość rekordów')
plt.ylabel('ilość faz')
plt.legend(['teoretyczna ilość faz', 'ilość faz wykonywana przez algorytm'])
plt.savefig(f'phases.png', dpi=300)
plt.close()
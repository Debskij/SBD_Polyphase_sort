import matplotlib.pyplot as plt
import math

from Entry import Entry

block_size = 50
max_record_size = 30
average_record_size = (max_record_size + 1) / 2
blocking_factor = block_size / average_record_size
# amount_of_rw_for_algorithm = [36, 44, 61, 58, 71, 77, 99, 81, 103, 130, 117, 136, 124, 156, 145, 195, 174, 212, 201, 259, 212, 233, 232, 251, 267, 246, 257, 319, 318, 289, 374, 328, 346, 370, 361, 392, 438, 394, 438, 426, 448, 408, 474, 484, 470, 479, 485, 492, 508, 544, 635, 589, 531, 579, 613, 598, 631, 700, 655, 649, 687, 662, 709, 685, 693, 725, 707, 745, 793, 785, 705, 808, 855, 825, 804, 850, 883, 791, 869, 935, 907, 837, 905, 929, 965, 1054, 1110, 925, 978, 1047, 1064, 976, 1006, 1156, 1075]
amount_of_rw_for_algorithm = []
record_samples = [2 * x for x in range(5, 100)]
e = Entry()
for amount_of_records in record_samples:
    amount_of_rw_for_algorithm.append(e.test_run_once(max_record_length=max_record_size,
                                                      amount_of_records=amount_of_records,
                                                      block_size=block_size,
                                                      file_to_generate='basic_test_fifth',
                                                      measure_rw_from_db=True))


def theoretical_input_output(records_count):
    return math.ceil(2 * records_count * (1.04 * math.log2(records_count) - 0.04) / blocking_factor)


theoretical_sum_rw = [theoretical_input_output(x) for x in record_samples]
print(amount_of_rw_for_algorithm)
plt.plot(record_samples, theoretical_sum_rw)
plt.plot(record_samples, amount_of_rw_for_algorithm)
plt.xlabel('ilość rekordów')
plt.ylabel('ilość read/write')
plt.legend(['teoretyczna ilość read/write', 'ilość read/write wykonywana przez algorytm'])
plt.savefig('filename.png', dpi=300)
plt.show()

# Прогамма поиска повсторов в WAV файле

from os.path import dirname, join as pjoin
from scipy.io import wavfile
import scipy.io
import math
import matplotlib.pyplot as plt
import numpy as np

# Задание начала и конца сегмента
segment_start_time = 55.57
segment_stop_time = 55.77

# Порог корреляции
corr_limit = 0.9

# Задание канала
channel = 0 # 0 - один канал, 1 - второй

# Open WAV file - не поддерживает почему то моно
wav_fname = './perehvat22050.wav'
samplerate, data = wavfile.read(wav_fname)
channels = data.shape[1]
length = data.shape[0]

# Вывод параметров файла
print("Число каналов =", channels)
print("Частота дискретизации =", samplerate)
print("Число отсчётов =", length)
print("Длительность секунд =", length/samplerate)

# Вычислим номер отсчёта начала и конца сегмента, длина сегмента
segment_start_number = int(segment_start_time * samplerate)
segment_stop_number = int(segment_stop_time * samplerate)
segment_length = segment_stop_number - segment_start_number

# Вывод параметров сегмента
print("Начало сегмента в секундах", segment_start_time)
print("Конец сегмента в секундах", segment_stop_time)
print("Начало сегмента в отсчётах", segment_start_number)
print("Конец сегмента в отсчётах", segment_stop_number)
print("Длина сегмента в отсчётах", segment_length)

# Поиск начала отсчётов
for i in range(0, (length - segment_length)):
    if data[i, channel] != 0:
        break;
start_file_number = i        
print("Начало отсчётов в файле", start_file_number)

# Проход по сегменту для вычисления среднего
sum_x = sum(data[segment_start_number:segment_stop_number, channel])
mean_x = sum_x / segment_length
print("Среднее для сегмента", mean_x)    

# Сумма квадратов отклонения
deviation_x = sum((data[segment_start_number:segment_stop_number, channel] - mean_x) ** 2)
print("Сумма квадратов отклонения для сегмента", deviation_x)    

# Процент прохода
percent_old = 0
percent = 0
percent_delta = 0

# Считаю корреляцию заданного сегмена по из файла по всему файлу/
# Для этого прохожу по заданному сегменту и по смещаему окну в файле
# Размер этого окна равен по длительности сегменту

# Считаю среднее для начала окна
# Потом не буду среднее пересчитывать заново, а буду корректировать
# Буду вычитать значение из начала окна, сдвигать окно, добавлять значение из конца окна
# Это сильно уменьшает число операций сложения
# По сравнению с версией где постоянный полный пересчёт среднего новый подход даёт выше скорость обработки
# При saplerate = 48000, размере выборки 16 бит и сегменте 0.01 сек даёт 1% обработки за 6 сек, против 8 секунд
sum_y = sum(data[start_file_number:(start_file_number + segment_length), channel])
mean_y = sum_y / segment_length

# Так же считаю сумму квадратов отклонения от среднего
# Но это не совсем верно, т.к. среднее меняется и по хорошему надо каждый раз по новому пересчитывать
# Сделаю допущение, что среднее меняется медленно
deviation_y = sum((data[start_file_number:(start_file_number + segment_length), channel] - mean_y) ** 2)

# Сумму произведения отклонения от средних к сожалению так нельзя считать, т.к. там все отсчёты сегмента приходятся на новые отсчёты окна

# Значения корреляции для вывода
corr_list = []

# Проход по файлу
for i in range(start_file_number, (length - segment_length - 1)):
    # Вывод процента обработки
    percent = i / (length - segment_length - start_file_number)
    percent_delta = percent - percent_old
    if percent_delta > 0.01:
        print("Выполнено %", percent)
        percent_old = percent
    # Сумма произведений отклонений от средних
    sum_mul_delta_x_y = sum((data[segment_start_number:segment_stop_number, channel] - mean_x) * (data[i:(i + segment_length), channel] - mean_y))
    # Корреляция
    correlation = sum_mul_delta_x_y / math.sqrt(deviation_x * deviation_y)
    # Добавим вычисленое значение в список
    corr_list.append(correlation)
    # Вывод отсчётов где корреляция выше порога
    if correlation > corr_limit:
        print("Корреляция", correlation, "Отсчёт", i)

    # Коррекция суммы квадратов отклонения от среднего, со старым средним
    deviation_y = deviation_y - ((data[i, channel] - mean_y) ** 2)
    
    # Коррекция среднего: вычитаю значение из начала окна и добавляю конец из смещённого окна
    sum_y = sum_y - data[i, channel]
    sum_y = sum_y + data[i + segment_length + 1, channel]
    mean_y = sum_y / segment_length
    
    # Коррекция суммы квадратов отклонения от среднего, с новым средним
    deviation_y = deviation_y + ((data[i + segment_length + 1, channel] - mean_y) ** 2)
    
# Вывод графика    
length = len(corr_list)
index = np.linspace(0., length, length)
plt.plot(index, corr_list[:], label="Channel")
plt.legend()
plt.xlabel("Номер отсчёта")
plt.ylabel("Коэффициент корреляции")
plt.show()
    
# Проход по файлу - нет полного пересчёта среднего
#for i in range(start_file_number, (length - segment_length)):
#    # Вывод процента обработки
#    percent = i / (length - segment_length - start_file_number)
#    percent_delta = percent - percent_old
#    if percent_delta > 0.01:
#        print(percent)
#        percent_old = percent
#    # Сумма квадратов отклонения
#    deviation_y = sum((data[i:(i + segment_length), channel] - mean_y) ** 2)
#    # Сумма произведений отклонений от средних
#    sum_mul_delta_x_y = sum((data[segment_start_number:segment_stop_number, channel] - mean_x) * (data[i:(i + segment_length), channel] - mean_y))
#    # Корреляция
#    correlation = sum_mul_delta_x_y / math.sqrt(deviation_x * deviation_y)
#    # Вывод отсчётов где корреляция выше порога
#    if correlation > corr_limit:
#        print("Корреляция", correlation, "Отсчёт", i)
#    
#    # Коррекция среднего: вычитаю значение из начала окна и добавляю конец из смещённого окна
#    sum_y = sum_y - data[i, channel]
#    sum_y = sum_y + data[i + segment_length + 1, channel]
#    mean_y = sum_y / segment_length

# Проход по файлу - старый код, полный долгий пересчёт
# for i in range(start_file_number, (length - segment_length)):
#    # Вывод процента обработки
#    percent = i / (length - segment_length - start_file_number)
#    percent_delta = percent - percent_old
#    if percent_delta > 0.01:
#        print(percent)
#        percent_old = percent
#    # Проход по сегменту для вычисления средних значений
#    sum_y = sum(data[i:(i + segment_length), channel])
#    mean_y = sum_y / segment_length
#    # Сумма квадратов отклонения
#    deviation_y = sum((data[i:(i + segment_length), channel] - mean_y) ** 2)
#    # Сумма произведений отклонений от средних
#    sum_mul_delta_x_y = sum((data[segment_start_number:segment_stop_number, channel] - mean_x) * (data[i:(i + segment_length), channel] - mean_y))
#    # Корреляция
#    correlation = sum_mul_delta_x_y / math.sqrt(deviation_x * deviation_y)
#    # Вывод отсчётов где корреляция выше порога
#    if correlation > corr_limit:
#        print("Корреляция", correlation, "Отсчёт", i)

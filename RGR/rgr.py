from multiprocessing.sharedctypes import synchronized

import numpy as np
import matplotlib.pyplot as plt

CRC_POLY = np.array([1, 1, 0, 1, 1, 1, 1, 0], dtype=int)
M = len(CRC_POLY) - 1
N = 10
FS = 1000

def ascii_encoder(text):
    bits = []
    for char in text:
        ascii_code = ord(char)
        if ascii_code > 127:
            raise ValueError("Символ не входит в ASCII")
        binary_code = format(ascii_code, '08b')
        for bit in binary_code:
            bits.append(int(bit))
    return np.array(bits, dtype=int)

def module2_division(bits, poly):
    remainder = bits.copy()
    m = len(poly)

    for i in range(len(remainder) - m + 1):
        if remainder[i] == 1:
            remainder[i:i + m] ^= poly

    return remainder[-(m - 1):]

def calculate_crc(data_bits, poly):
    crc_length = len(poly) - 1
    extended_bits = np.concatenate((data_bits, [0] * crc_length))
    return module2_division(extended_bits, poly)

def check_crc(packet, poly):
    remainder = module2_division(packet, poly)
    return np.all(remainder == 0)

def generate_gold(student_number):
    x = [int(bit) for bit in format(student_number, '05b')]
    y = [int(bit) for bit in format(student_number + 7, '05b')]
    G = 2**5 -1
    gold = []
    for i in range(G):
        output = x[4] ^ y[4]
        gold.append(output)

        feedback_x = x[3] ^ x[4]
        feedback_y = y[1] ^ y[4]

        x = [feedback_x] + x[:-1]
        y = [feedback_y] + y[:-1]

    return np.array(gold, dtype=int)

def bits_to_samples(bits, N):
    samples = np.repeat(bits, N)
    return samples

def add_delay(samples, delay):
    K = len(samples)
    if not 0 <= delay <= K:
        raise ValueError(f"Смещение должно быть от 0 до {K}")
    signal = np.zeros(2 * K, dtype=int)
    signal[delay:delay + K] = samples
    return signal

def input_delay(K):
    while True:
        try:
            delay = int(input(f"Введите смещение от 0 до {K}: "))
            if 0 <= delay <= K:
                return delay
            print("Смещение вне допустимого диапазона")
        except ValueError:
            print("Необходимо ввести целое число")

def add_noise(signal, sigma):
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("Некорректное значение sigma")
    noise = np.random.normal(loc=0, scale=sigma, size=len(signal))
    rx_samples = signal + noise
    return rx_samples, noise

def input_sigma():
    while True:
        try:
            sigma = float(input("Введите СКО шума sigma: "))
            if sigma >= 0:
                return sigma
            print("Sigma должно быт конечным и неотрицательным")
        except ValueError:
            print("Необходимо ввести вещественное число")

def correlation_calc(rx_samples, reference):
    Q = len(rx_samples)
    K_G = len(reference)
    correlation = np.zeros(Q - K_G + 1)
    for k in range(Q - K_G + 1):
        total = 0.0
        for n in range(K_G):
            total += rx_samples[k + n] * reference[n]
        correlation[k] = total / K_G
    return correlation

def correlation_receiver(rx_samples, gold, N, packet_length):
    gold_samples = bits_to_samples(gold, N)
    reference = 2 * gold_samples - 1
    rx_bipolar = 2 * rx_samples - 1
    K_G = len(reference)
    correlation = np.correlate(rx_bipolar, reference, mode="valid") / K_G
    detected_delay = int(np.argmax(correlation))
    synchronized_signal = rx_samples[detected_delay:]
    return detected_delay, synchronized_signal, correlation

def decision_receiver(signal, N, bit_count):
    P = N / 2
    K = N * bit_count
    signal = signal[:K]
    received_bits = np.zeros(bit_count, dtype=int)
    sums = np.zeros(bit_count, dtype=float)
    for k in range(bit_count):
        total = 0.0
        for i in range(N):
            total += signal[k * N + i]
        sums[k] = total
        if total >= P:
            received_bits[k] = 1
        else:
            received_bits[k] = 0
    return received_bits, sums

def calculate_ber(tx_bits, rx_bits):
    if len(tx_bits) != len(rx_bits):
        raise ValueError("Длины массивов не совпадают")
    if len(tx_bits) == 0:
        raise ValueError("Пустая последовательность")
    errors = np.count_nonzero(tx_bits != rx_bits)
    ber = errors / len(tx_bits)
    return errors, ber

def ascii_decoder(bits):
    if len(bits) % 8 != 0:
        raise ValueError("Количество битов не кратно 8")
    text = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        binary_string = "".join(map(str, byte))
        ascii_code = int(binary_string, 2)
        text += chr(ascii_code)
    return text

def calculate_spectrum(samples, fs):
    K = len(samples)
    spectrum = np.zeros(K, dtype=complex)
    for k in range(K):
        real_sum = 0.0
        imag_sum = 0.0
        for n in range(K):
            angle = -2 * np.pi * k * n / K
            real_sum += samples[n] * np.cos(angle)
            imag_sum += samples[n] * np.sin(angle)
        spectrum[k] = real_sum + 1j * imag_sum
    amplitude = np.abs(spectrum) / K
    frequencies = np.fft.fftfreq(K, 1 / fs)
    frequencies = np.fft.fftshift(frequencies)
    amplitude = np.fft.fftshift(amplitude)
    return frequencies, amplitude

def plot_bits(bits, title):
    x = np.arange(len(bits) + 1)
    y = np.append(bits, bits[-1])

    plt.figure(figsize=(14, 3))
    plt.step(x, y, where="post")

    plt.title(title)
    plt.xlabel("Номер бита")
    plt.ylabel("Значение бита")

    plt.yticks([0, 1])
    plt.ylim(-0.2, 1.2)
    plt.xlim(0, len(bits))
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.show()

def plot_packet(gold, data_bits, crc):
    G = len(gold)
    L = len(data_bits)
    M = len(crc)

    plt.figure(figsize=(16, 4))

    segments = [
        (gold, 0, "green", "Синхросигнал"),
        (data_bits, G, "blue", "Информационные биты"),
        (crc, G + L, "red", "CRC")
    ]

    for bits, start, color, label in segments:
        x = np.arange(start, start + len(bits) + 1)
        y = np.append(bits, bits[-1])

        plt.step(x, y, where="post", color=color, label=label)

    plt.axvline(G, color="black", linestyle="--")
    plt.axvline(G + L, color="black", linestyle="--")

    plt.title("Полный передаваемый пакет")
    plt.xlabel("Номер бита")
    plt.ylabel("Значение бита")

    plt.yticks([0, 1])
    plt.ylim(-0.2, 1.2)
    plt.xlim(0, G + L + M)

    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_samples(samples, N, fs):
    K = len(samples)
    t = np.arange(K) / fs

    fig, axes = plt.subplots(2, 1, figsize=(15, 7))

    axes[0].step(np.arange(K + 1) / fs, np.append(samples, samples[-1]), where="post")
    axes[0].set_title("Передаваемый сигнал во временной области")
    axes[0].set_xlabel("Время, с")
    axes[0].set_ylabel("Амплитуда")
    axes[0].set_yticks([0, 1])
    axes[0].set_ylim(-0.2, 1.2)
    axes[0].set_xlim(0, K / fs)
    axes[0].grid(True, alpha=0.3)

    count = min(15 * N, K)

    axes[1].stem(t[:count], samples[:count])

    for i in range(0, count + 1, N):
        axes[1].axvline(i / fs, color="gray", linestyle="--", alpha=0.5)

    axes[1].set_title("Временные отсчёты первых 15 битов")
    axes[1].set_xlabel("Время, с")
    axes[1].set_ylabel("Амплитуда")
    axes[1].set_yticks([0, 1])
    axes[1].set_ylim(-0.2, 1.2)
    axes[1].set_xlim(0, count / fs)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def plot_delayed_signal(signal, delay, K, fs):
    t = np.arange(len(signal) + 1) / fs

    plt.figure(figsize=(15, 4))

    plt.step(t, np.append(signal, signal[-1]), where="post", label="Передаваемый сигнал")

    plt.axvspan(delay / fs, (delay + K) / fs, color="green", alpha=0.1, label="Область пакета")
    plt.axvline(delay / fs, color="green", linestyle="--", label="Начало пакета")
    plt.axvline((delay + K) / fs, color="red", linestyle="--", label="Конец пакета")

    plt.title("Сигнал с временной задержкой")
    plt.xlabel("Время, с")
    plt.ylabel("Амплитуда")

    plt.yticks([0, 1])
    plt.ylim(-0.2, 1.2)
    plt.xlim(0, len(signal) / fs)

    plt.grid(True, alpha=0.3)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()

def plot_noisy_signal(signal, noise, rx_samples, fs, sigma):
    t = np.arange(len(signal)) / fs

    fig, axes = plt.subplots(3, 1, figsize=(15, 9), sharex=True)

    axes[0].step(t, signal, where="post", color="blue")
    axes[0].set_title("Исходный сигнал")
    axes[0].set_ylabel("Амплитуда")
    axes[0].set_ylim(-0.2, 1.2)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, noise, color="orange", linewidth=0.8)
    axes[1].axhline(0, color="black", linestyle="--")
    axes[1].set_title(f"Гауссовский шум (μ = 0, σ = {sigma})")
    axes[1].set_ylabel("Амплитуда")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, rx_samples, color="green", linewidth=0.8)
    axes[2].set_title("Принятый зашумлённый сигнал")
    axes[2].set_xlabel("Время, с")
    axes[2].set_ylabel("Амплитуда")
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim(0, len(signal) / fs)

    plt.tight_layout()
    plt.show()

def plot_channel_spectra(signal, rx_samples, fs):
    f_tx, A_tx = calculate_spectrum(signal, fs)
    f_rx, A_rx = calculate_spectrum(rx_samples, fs)

    fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True, sharey=True)

    axes[0].plot(f_tx, A_tx, color="blue")
    axes[0].set_title("Амплитудный спектр переданного сигнала")
    axes[0].set_ylabel("Амплитуда")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(f_rx, A_rx, color="orange")
    axes[1].set_title("Амплитудный спектр принятого зашумлённого сигнала")
    axes[1].set_xlabel("Частота, Гц")
    axes[1].set_ylabel("Амплитуда")
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim(-fs / 2, fs / 2)

    plt.tight_layout()
    plt.show()

def plot_symbol_duration_spectra(bits, N, fs):
    if N < 2 or N % 2 != 0:
        raise ValueError(
            "Для точного уменьшения вдвое N должно быть чётным")
    N_values = [N // 2, N, N * 2]
    colors = ["blue", "green", "red"]
    plt.figure(figsize=(15, 6))

    for n, color in zip(N_values, colors):
        samples = bits_to_samples(bits, n)
        frequencies, amplitude = calculate_spectrum(samples, fs)
        Tb = n / fs

        plt.plot(frequencies, amplitude, color=color, alpha=0.8, label=f"N = {n}, Tb = {Tb * 1000:.1f} мс")

    plt.title("Сравнение спектров при различной длительности символа")
    plt.xlabel("Частота, Гц")
    plt.ylabel("Амплитуда")
    plt.xlim(-fs / 2, fs / 2)

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def main():
    text = input("Введите имя латиницей: ")
    if not text:
        print("Пустая строка")
        return
    data_bits = ascii_encoder(text)
    L = len(data_bits)
    print("\n === Блок 1: ASCII-кодер ===")
    print("Исходный текст:", text)
    print("Количество символов:", len(text))
    print("Количество бит L:", L)
    print("Битовая последовательность:")
    print(data_bits)
    plot_bits(data_bits, "Информационная последовательность")

    crc = calculate_crc(data_bits, CRC_POLY)
    packet = np.concatenate((data_bits, crc))
    print("\n === Блок 2: Вычисление CRC ===")
    print("Порождающий полином:", CRC_POLY)
    print("Длина CRC M:", M)
    print("CRC:", "".join(map(str, crc)))
    print("Длина пакета L + M:", len(packet))
    print("Пакет с CRC:", packet)
    remainder = module2_division(packet, CRC_POLY)
    print("Остаток от деления: ", remainder)
    if check_crc(packet, CRC_POLY):
        print("Ошибок не обнаружено")
    else:
        print("Обнаружена ошибка")

    gold = generate_gold(12)
    G = len(gold)
    full_packet = np.concatenate([gold, packet])
    print("\n === Блок 3: Последовательность Голда ===")
    print("Длина G:", G)
    print("Последовательность Голда:")
    print("".join(map(str, gold)))
    print("\nПолный передаваемый пакет")
    print("Длина синхросигнала G:", G)
    print("Длина данных L:", L)
    print("Длина CRC M:", M)
    print("Общая длина:", len(full_packet))
    print("Полный пакет:")
    print("".join(map(str, full_packet)))
    plot_packet(gold, data_bits, crc)

    tx_samples = bits_to_samples(full_packet, N)
    K = len(tx_samples)
    Ts = 1 / FS
    Tb = N / FS
    duration = K / FS
    print("\n=== Блок 4: Формирование временных отсчётов ===")
    print("Количество битов:", len(full_packet))
    print("Отсчётов на бит N:", N)
    print("Частота дискретизации:", FS, "Гц")
    print("Период дискретизации:", Ts, "с")
    print("Длительность бита:", Tb, "с")
    print("Количество отсчётов:", K)
    print("Длительность сигнала:", duration, "с")
    print("Первые 100 отсчётов:")
    print(tx_samples[:100])
    assert K == N * (L + M + G)
    plot_samples(tx_samples, N, FS)

    K = len(tx_samples)
    delay = input_delay(K)
    signal = add_delay(tx_samples, delay)
    print("\n=== Блок 5: Сигнал с временно задержкой ===")
    print("Длина исходного сигнала:", K)
    print("Длина нового массива:", len(signal))
    print("Смещение:", delay, "отсчётов")
    print("Временная задержка:", delay / FS, "с")
    print("Начальный индекс:", delay)
    print("Конечный индекс:", delay + K - 1)
    print("Нулей перед пакетом:", delay)
    print("Нулей после пакета:", K - delay)
    print("Общая длительность:", len(signal) / FS, "с")
    plot_delayed_signal(signal, delay, K, FS)

    sigma = input_sigma()
    rx_samples, noise = add_noise(signal, sigma)
    print("\n=== Блок 6: Моделирование радиоканала ===")
    print("Частота дискретизации:", FS, "Гц")
    print("Заданное математическое ожидание:", 0)
    print("Заданное СКО:", sigma)
    print("Теоретическая дисперсия:", sigma**2)
    plot_noisy_signal(signal, noise, rx_samples, FS, sigma)

    detected_delay, synchronized_signal, correlation = correlation_receiver(rx_samples, gold, N, len(tx_samples))
    print("\n=== Блок 7: Корреляционный прием === ")
    print("Фактическое смещение:", delay)
    print("Найденное смещение:", detected_delay)
    print("Максимум корреляции:", correlation[detected_delay])
    print("Найденная временная задержка:", detected_delay / FS, "с")
    print("Ошибка синхронизации:", abs(detected_delay - delay), "отсчётов")
    print("Длина сигнала до синхронизации:",len(rx_samples))
    print("Длина сигнала после синхронизации:", len(synchronized_signal))
    if detected_delay == delay:
        print("Синхронизация выполнена успешно")
    else:
        print("Обнаружена ошибка синхронизации")

    bit_count = L + M + G
    P = N / 2
    received_bits, sums = decision_receiver(synchronized_signal, N, bit_count)
    print("\n=== Блок 8: Пороговое принятие решения ===")
    print("Отсчетов на бит N: ", N)
    print("Порог P: ", P)
    print("Количество входных отсчетов: ", N * bit_count)
    print("Количесво отброшенных отсчетов: ", len(synchronized_signal) - N * bit_count)
    print("Количество восстановленных битов: ", len(received_bits))
    errors, ber = calculate_ber(full_packet, received_bits)
    print("Количество битовых ошибок:", errors)
    print(f"Экспериментальный BER: {ber:.6f}")
    print(f"Экспериментальный BER: {ber * 100:.4f}%")

    received_packet = received_bits[G:]
    print("\n=== Блок 9: Удаление синхропоследовательности ===")
    print("Количество удалённых битов:", G)
    print("Длина оставшегося пакета:", len(received_packet))
    print("Полученный пакет:")
    print("".join(map(str, received_packet)))

    remainder = module2_division(received_packet, CRC_POLY)
    crc_valid = check_crc(received_packet, CRC_POLY)
    print("\n=== Блок 10: Проверка CRC ===")
    print("Порождающий полином:", CRC_POLY)
    print("Принятый CRC:", received_packet[-M:])
    print("Остаток от деления:", remainder)
    if crc_valid:
        print("Ошибок не обнаружено!")
        received_data = received_packet[:-M]
        decoded_text = ascii_decoder(received_data)
        print("\n=== Блок 11: ASCII-декодирование ===")
        print("Количество информационных битов:", len(received_data))
        print("Количество символов:", len(decoded_text))
        print("Исходный текст:", text)
        print("Восстановленный текст:", decoded_text)
        if decoded_text == text:
            print("Текст успешно восстановлен")
        else:
            print("Восстановленный текст отличается от исходного")
    else:
        print("Обнаружена ошибка передачи")
        print("ASCII-декодирование не выполняется")

    print("\n=== Блок 12: Спектральный анализ ===")
    print("Частота дискретизации:", FS, "Гц")
    print("Частотное разрешение:", FS / len(signal), "Гц")
    plot_channel_spectra(signal, rx_samples, FS)
    print("\n= Влияние длительности символа =")
    for n in [N // 2, N, N * 2]:
        Tb = n / FS
        Rb = FS / n
        K = len(full_packet) * n
        print(f"\nN = {n}")
        print(f"Длительность символа: {Tb:.4f} с")
        print(f"Битовая скорость: {Rb:.2f} бит/с")
        print(f"Количество отсчётов: {K}")
        print(f"Длительность пакета: {K / FS:.4f} с")
        print(f"Частотное разрешение: {FS / K:.4f} Гц")
        print(f"Первый нуль огибающей: {1 / Tb:.2f} Гц")
        print(f"Ширина главного лепестка: {2 / Tb:.2f} Гц")
    plot_symbol_duration_spectra(full_packet, N, FS)

if __name__ == "__main__":
    main()

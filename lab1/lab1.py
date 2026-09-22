import numpy as np
import matplotlib.pyplot as plt

harmonics = [
    (7, 16, np.pi / 13),
    (7, 4 * 16, np.pi / 13)
]

duration = 1.0
n_bits = 3

def calc_freq_max(harmonics):
    return max(h[1] for h in harmonics)

def kotelnikov_theorem(freq_max):
    f_s = freq_max * 2 + 10
    return f_s

def generate_signal(t, harmonics):
    y = np.zeros_like(t, dtype=float)
    for A, f, phi in harmonics:
        y += A * np.cos(2 * np.pi * f * t + phi)
    return y

def adc(f_s, duration, harmonics):
    N = int(np.ceil(f_s * duration))
    t_samples = np.arange(N) / f_s
    y_samples = generate_signal(t_samples, harmonics)
    return t_samples, y_samples

def dft(y_samples):
    N = len(y_samples)
    Y = np.zeros(N, dtype=complex)
    for k in range(N):
        real_sum = 0.0
        imag_sum = 0.0
        for n in range(N):
            angle = -2 * np.pi * k * n / N
            real_sum += y_samples[n] * np.cos(angle)
            imag_sum += y_samples[n] * np.sin(angle)
        Y[k] = real_sum + 1j * imag_sum
    return Y

def amp_spectrum(Y, f_s):
    N = len(Y)
    amp = np.abs(Y) / N
    freqs = np.arange(N) * f_s / N
    return amp, freqs

def bandwidth(f_s, N):
    delta_f = f_s / N
    return delta_f

def calc_memory(y_samples):
    N = len(y_samples)
    memory_float64 = N * 8
    print(f"Объем памяти для float64 = {memory_float64} байт")

    memory_int16 = N * 2
    print(f"Объем памяти для int16 = {memory_int16} байт")


def rft(Y):
    N = len(Y)
    y = np.zeros(N, dtype=complex)
    for n in range(N):
        real_sum = 0.0
        imag_sum = 0.0
        for k in range(N):
            angle = 2 * np.pi * k * n / N
            real_sum += Y[k].real * np.cos(angle) - Y[k].imag * np.sin(angle)
            imag_sum += Y[k].real * np.sin(angle) + Y[k].imag * np.cos(angle)
        y[n] = (real_sum + 1j * imag_sum) / N
    return y

def adc_quantization(y_samples, n_bits):
    y_min = np.min(y_samples)
    y_max = np.max(y_samples)

    n_levels = 2 ** n_bits
    delta = (y_max - y_min) / (n_levels - 1)

    y_quant = np.round((y_samples - y_min) / delta) * delta + y_min
    y_quant = np.clip(y_quant, y_min, y_max)

    return y_quant, delta

def aver_error(y_samples, y_quant, delta):
    error = y_samples - y_quant
    avg_error = np.mean(np.abs(error))
    rms = delta / np.sqrt(12)
    return avg_error, rms


def show_plot(f_s, t_samples, y_samples, y_restored, freqs, amp, amp_quant, harmonics):
    t_cont = np.linspace(0, duration, 2000)
    y_cont = generate_signal(t_cont, harmonics)

    half = len(y_samples) // 2

    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(12, 8))

    ax1.plot(t_cont, y_cont, 'b-', linewidth=1.2)
    ax1.set_ylabel('Амплитуда')
    ax1.set_title('Непрерывный сигнал')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, duration)

    ax2.stem(t_samples, y_samples, linefmt='r-', markerfmt='ro', basefmt='k-')
    ax2.set_xlabel('Время, с')
    ax2.set_ylabel('Амплитуда')
    ax2.set_title(f'Дискретизированный сигнал')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, duration)

    ax3.stem(freqs[:half], amp[:half], linefmt='g-', markerfmt='go', basefmt='k-')
    ax3.set_xlabel('Частота, Гц')
    ax3.set_ylabel('Амплитуда')
    ax3.set_title('Амплитудный спектр (после прямого ПФ)')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, f_s / 2)

    ax4.plot(t_samples, y_restored.real, 'm-', linewidth=1.5, marker='o', markersize=4, label='Восстановленный сигнал')
    ax4.set_xlabel('Время, с')
    ax4.set_ylabel('Амплитуда')
    ax4.set_title('Восстановленный сигнал (после обратного ПФ)')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, duration)

    ax5.stem(freqs[:half], amp_quant[:half], linefmt='r-', markerfmt='ro', basefmt='k-')
    ax5.set_title(f'Спектр после квантования ({n_bits} бит)')
    ax5.set_xlabel('Частота, Гц')
    ax5.set_ylabel('Амплитуда')
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim(0, f_s / 2)

    plt.tight_layout()
    plt.show()

def main():
    freq_max = calc_freq_max(harmonics)
    f_s = kotelnikov_theorem(freq_max)
    print(f"Максимальная частота сигнала: {freq_max} Гц")
    print(f"Частота дискретизации: {f_s} Гц")

    t_samples, y_samples = adc(f_s, duration, harmonics)
    print(f"Количество отсчётов: {len(y_samples)}")

    Y = dft(y_samples)
    amp, freqs = amp_spectrum(Y, f_s)

    width = bandwidth(f_s, len(y_samples))
    print(f"Ширина спектра = {width:.2f} Гц")

    calc_memory(y_samples)

    y_restored = rft(Y)

    y_quant, delta = adc_quantization(y_samples, n_bits)

    Y_quant = dft(y_quant)
    amp_quant, _ = amp_spectrum(Y_quant, f_s)

    for n in [3, 4, 5, 6]:
        y_quant, delta = adc_quantization(y_samples, n)
        avg_error, rms = aver_error(y_samples, y_quant, delta)
        print(f"Разрядность АЦП: {n}, средняя ошибка: {rms:.2f}")

    show_plot(f_s, t_samples, y_samples, y_restored, freqs, amp, amp_quant, harmonics)


if __name__ == '__main__':
    main()

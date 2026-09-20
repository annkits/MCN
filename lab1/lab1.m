[y, Fs] = audioread('sample.wav');
duration = 48.303;

N = size(y, 1);

Fs_calc = N / duration;

fprintf('Частота дискретизации Fs (выданная) = %d Гц\n', Fs);
fprintf('Частота дискретизации Fs (вычисленная) = %.4f Гц\n', Fs_calc);
fprintf('Число отсчётов N = %d\n', length(y));
fprintf('Длительность = %.3f с\n', duration);
fprintf('Число каналов = %d\n', size(y, 2));

if size(y, 2) > 1
    y = y(:, 1);
end

y1 = downsample(y, 80);
Fs1 = Fs / 80;
zvuk = audioplayer(y1, Fs1);
play(zvuk);

N1 = length(y);
Y1 = fft(y);
f1 = (0:N1-1) * Fs / N1;
amp1 = abs(Y1) / N1;
half1 = floor(N1/2);

N2 = length(y1);
Y2 = fft(y1);
f2 = (0:N2-1) * Fs1 / N2;
amp2 = abs(Y2) / N2;
half2 = floor(N2/2);

subplot(2,1,1);
plot(f1(1:half1), amp1(1:half1));
xlabel('Частота, Гц'); ylabel('Амплитуда');
title(sprintf('Спектр оригинала, Fs = %d Гц', Fs));
grid on;
xlim([0, Fs1/2]);

subplot(2,1,2);
plot(f2(1:half2), amp2(1:half2));
xlabel('Частота, Гц'); ylabel('Амплитуда');
title(sprintf('Спектр прореженного сигнала, Fs = %d Гц', Fs1));
grid on;
xlim([0, Fs1/2]);
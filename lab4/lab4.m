%% Генерация последовательностей Голда (рис. 4.5)

% Функция генерации одной последовательности Голда
function gold = generate_gold(x_init, y_init)
    x = x_init;
    y = y_init;
    gold = zeros(1, 31);
    
    for i = 1:31
        gold(i) = xor(x(5), y(5));          % выход = x5 XOR y5
        
        new_x = xor(x(4), x(5));            % обратная связь x4, x5
        new_y = xor(y(2), y(5));            % обратная связь y2, y5
        
        % сдвиг вправо
        x = [new_x, x(1:4)];
        y = [new_y, y(1:4)];
    end
end

% Исходные данные (номер 12)
x1 = [0 1 1 0 0];   % 01100
y1 = [1 0 0 1 1];   % 10011

% Новые данные (x+1, y-5)
x2 = [0 1 1 0 1];   % 01101
y2 = [0 1 1 1 0];   % 01110

seq1 = generate_gold(x1, y1);   % исходная
seq2 = generate_gold(x2, y2);   % новая

disp('Исходная последовательность Голда:');
disp(num2str(seq1));
disp('Новая последовательность Голда:');
disp(num2str(seq2));

%% Пункт 5: Автокорреляция и взаимная корреляция

% Переводим в ±1
s1 = 2*seq1 - 1;
s2 = 2*seq2 - 1;

% Автокорреляция
[acf, lags] = xcorr(s1, 'normalized');   % нормированная

fprintf('\nАвтокорреляция:\n');
fprintf('Сдвиг | Автокорреляция\n');
fprintf('------|---------------\n');
for i = 1:length(lags)
    if lags(i) >= 0
        fprintf('%5d | % .5f\n', lags(i), acf(i));
    end
end

% Взаимная корреляция
[ccf, lags_c] = xcorr(s1, s2, 'normalized');

fprintf('\nВзаимная корреляция:\n');
fprintf('Сдвиг | Взаимная корреляция\n');
fprintf('------|--------------------\n');
for i = 1:length(lags_c)
    if lags_c(i) >= 0
        fprintf('%5d | % .5f\n', lags_c(i), ccf(i));
    end
end

%% Пункт 6: График автокорреляции

figure('Name', 'Автокорреляция последовательности Голда', 'NumberTitle', 'off');
stem(lags, acf, 'filled', 'LineWidth', 1.2);
grid on;
xlabel('Задержка (lag)');
ylabel('Нормированная автокорреляция R(\tau)');
title('Автокорреляционная функция последовательности Голда (номер 12)');
xlim([-30 30]);
ylim([-0.5 1.1]);

hold on;
yline(0, '--k', 'Alpha', 0.3);
yline(1, '--r', 'Alpha', 0.4);
hold off;

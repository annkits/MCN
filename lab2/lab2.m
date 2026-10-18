%% 1. Исходные данные из методички
P_BS = 46;              % мощность передатчика BS, дБм
P_UE = 24;              % мощность передатчика UE, дБм
G_BS = 21;              % усиление антенны BS, дБи
PenetrationM = 15;      % запас на проникновение, дБ
IM = 1;                 % запас на интерференцию, дБ
f_MHz = 1800;            % частота, МГц
f_GHz = f_MHz/1000;      % частота, ГГц
BW_UL = 10e6;            % полоса UL, Гц
BW_DL = 20e6;            % полоса DL, Гц
NF_BS = 2.4;             % коэффициент шума BS, дБ
NF_UE = 6;               % коэффициент шума UE, дБ
SINR_UL = 4;             % требуемый SINR UL, дБ
SINR_DL = 2;             % требуемый SINR DL, дБ
MIMO_Gain = 3;            % выигрыш MIMO 2x2, дБ
FeederLoss = 2;           % потери фидера, дБ
LNA_Loss = 0.4;           % потери МШУ, дБ
JumperLoss = 0.5;         % потери джампера, дБ
L_total = FeederLoss + LNA_Loss + JumperLoss;
Nsectors = 3;
Area_macro = 100;         % площадь макротерритории, км^2
Area_indoor = 4;          % площадь ТЦ/БЦ, км^2

%% 2. Бюджет каналов UL и DL
Noise_UL = -174 + 10*log10(BW_UL);
Noise_DL = -174 + 10*log10(BW_DL);

RxSens_BS = NF_BS + Noise_UL + SINR_UL;
RxSens_UE = NF_UE + Noise_DL + SINR_DL;

MAPL_UL = P_UE - L_total + G_BS + MIMO_Gain - IM - PenetrationM - RxSens_BS;
MAPL_DL = P_BS - L_total + G_BS + MIMO_Gain - IM - PenetrationM - RxSens_UE;

fprintf('\nБЮДЖЕТ КАНАЛОВ\n');
fprintf('Тепловой шум UL       = %.2f дБм\n', Noise_UL);
fprintf('Тепловой шум DL       = %.2f дБм\n', Noise_DL);
fprintf('Чувствительность BS   = %.2f дБм\n', RxSens_BS);
fprintf('Чувствительность UE   = %.2f дБм\n', RxSens_UE);
fprintf('MAPL_UL               = %.2f дБ\n', MAPL_UL);
fprintf('MAPL_DL               = %.2f дБ\n', MAPL_DL);

%% 3. Дополнительные параметры моделей
fprintf('\nВведите параметры местности для моделей, отсутствующие в задании.\n');
hBS = input('Высота антенны BS, м (для COST231 и W-I): ');
hMS = input('Высота антенны UE, м (для COST231 и W-I): ');
terrain = input('Тип местности COST231: 1=DU, 2=U, 3=SU, 4=RURAL, 5=ROAD: ');
hBuilding = input('Средняя высота зданий h, м (Walfish-Ikegami): ');
streetWidth = input('Средняя ширина улиц w, м (Walfish-Ikegami): ');
buildingSpacing = input('Среднее расстояние между зданиями b, м (Walfish-Ikegami): ');
phi = input('Средний угол phi в градусах (Walfish-Ikegami, 0...90): ');

%% 4. Диапазон расстояний
% Для UMiNLOS расстояние задаётся в метрах.
d_m = logspace(log10(1), log10(2000), 1000);
PL_UMi = 26*log10(f_GHz) + 22.7 + 36.7*log10(d_m);

% Для COST231 Hata расстояние задаётся в километрах.
d_km = logspace(log10(0.03), log10(20), 1000);
if f_MHz <= 1500
    A = 69.55; B = 26.16;
else
    A = 46.3; B = 33.9;
end

% Поправка на высоту мобильной станции a(hMS).
if terrain == 1 || terrain == 2
    a_hMS = 3.2*(log10(11.75*hMS))^2 - 4.97;
else
    a_hMS = (1.1*log10(f_MHz)-0.7)*hMS - (1.56*log10(f_MHz)-0.8);
end

switch terrain
    case 1      % Dense Urban
        Lclutter = 3;
    case 2      % Urban
        Lclutter = 0;
    case 3      % Suburban
        Lclutter = -(2*log10(f_MHz/28)^2 + 5.4);
    case 4      % Rural
        Lclutter = -(4.78*(log10(f_MHz))^2 -18.33*log10(f_MHz)+40.94);
    case 5      % Road
        Lclutter = -(4.78*(log10(f_MHz))^2 -18.33*log10(f_MHz)+35.94);
    otherwise
        error('Тип местности должен быть числом от 1 до 5.');
end

s = zeros(size(d_km));
s(d_km >= 1) = 44.9 - 6.55*log10(f_MHz);
s(d_km < 1)  = (47.88 + 13.9*log10(f_MHz) - 13.9*log10(hBS)) / log10(50);

PL_COST = A + B*log10(f_MHz) - 13.82*log10(hBS) - a_hMS + s.*log10(d_km) + Lclutter;

%% 5. Walfish-Ikegami: LOS и приближённая NLOS
PL_WI_LOS = 42.6 + 20*log10(f_MHz) + 26*log10(d_km);

deltaH = hBuilding - hMS;
L0 = 32.44 + 20*log10(f_MHz) + 20*log10(d_km);

if phi < 35
    Lori = -10 + 0.354*phi;
elseif phi < 55
    Lori = 2.5 + 0.075*(phi-35);
else
    Lori = 4.0 - 0.114*(phi-55);
end

L2 = -16.9 - 10*log10(streetWidth) + 10*log10(f_MHz) ...
     + 20*log10(max(abs(deltaH), 0.01)) + Lori;

if hBS > hBuilding
    L11 = -18*log10(1 + hBS - hBuilding);
    ka = 54;
    kd = 18;
else
    L11 = 0;
    ka = 54 - 0.8*(hBS-hBuilding).*min(d_km/0.5, 1);
    kd = 18 - 15*(hBS-hBuilding)/max(abs(deltaH),0.01);
end
kf = -4 + 0.7*(f_MHz/925 - 1);
L1 = L11 + ka + kd.*log10(d_km) + kf*log10(f_MHz) ...
     - 9*log10(buildingSpacing);
PL_WI_NLOS = L0 + max(L1 + L2, 0);

%% 6. График моделей распространения
figure('Name','Макросеть: Радиус и модели','Color','w');
semilogx(d_km*1000, PL_COST, 'LineWidth', 1.8); hold on;
semilogx(d_km*1000, PL_WI_LOS, '--', 'LineWidth', 1.5);
semilogx(d_km*1000, PL_WI_NLOS, '-.', 'LineWidth', 1.8);
yline(MAPL_UL, ':', 'MAPL UL', 'LineWidth', 1.4);
yline(MAPL_DL, ':', 'MAPL DL', 'LineWidth', 1.4);
grid on;
xlim([100, 20000]);
ylim([80, 180]);
xlabel('Расстояние от BS, м');
ylabel('Потери радиосигнала PL, дБ');
title('Модели распространения для макросети (COST231 и W-I)');
legend('COST231 Hata', 'W-I LOS', 'W-I NLOS', 'MAPL UL', 'MAPL DL', 'Location', 'best');

figure('Name','Микросеть: Indoor / UMiNLOS','Color','w');
semilogx(d_m, PL_UMi, 'r-', 'LineWidth', 2); hold on;
yline(MAPL_UL, ':', 'MAPL UL', 'LineWidth', 1.4);
yline(MAPL_DL, ':', 'MAPL DL', 'LineWidth', 1.4);
grid on;
xlim([1, 500]);
ylim([20, 160]);
xlabel('Расстояние от BS, м');
ylabel('Потери радиосигнала PL, дБ');
title('Модель UMiNLOS для микро- и indoor-сетей');
legend('UMiNLOS', 'MAPL UL', 'MAPL DL', 'Location', 'best');

%% 7. Радиусы по пересечению PL(d) и MAPL
% UMiNLOS применяется для indoor/micro/femto. d задано в метрах.
radius_UMi_UL = findRadius(d_m, PL_UMi, MAPL_UL);
radius_UMi_DL = findRadius(d_m, PL_UMi, MAPL_DL);

% Для COST231 и Walfish d задано в км; результат переводится в км.
radius_COST_UL = findRadius(d_km, PL_COST, MAPL_UL);
radius_COST_DL = findRadius(d_km, PL_COST, MAPL_DL);
radius_WI_UL = findRadius(d_km, PL_WI_NLOS, MAPL_UL);
radius_WI_DL = findRadius(d_km, PL_WI_NLOS, MAPL_DL);

fprintf('\nРАДИУСЫ СОТ\n');
fprintf('UMiNLOS: UL = %.2f м, DL = %.2f м\n', ...
        radius_UMi_UL, radius_UMi_DL);
fprintf('COST231 Hata: UL = %.3f км, DL = %.3f км\n', ...
        radius_COST_UL, radius_COST_DL);
fprintf('Walfish-Ikegami NLOS: UL = %.3f км, DL = %.3f км\n', ...
        radius_WI_UL, radius_WI_DL);

%% 8. Площадь сайта и число базовых станций
% Для макросети используем COST231 Hata.
R_macro = min(radius_COST_UL, radius_COST_DL);
S_macro = 1.95*R_macro^2;
N_macro = ceil(Area_macro/S_macro);

% Для indoor/микро-/фемтосети используем UMiNLOS.
R_indoor_km = min(radius_UMi_UL, radius_UMi_DL)/1000;
S_indoor = 1.95*R_indoor_km^2;
N_indoor = ceil(Area_indoor/S_indoor);

fprintf('\nРАСЧЁТ КОЛИЧЕСТВА САЙТОВ\n');
fprintf('Макросеть: R = %.3f км, площадь сайта = %.3f км^2, N = %d\n', ...
        R_macro, S_macro, N_macro);
fprintf('Indoor/микросеть: R = %.2f м, площадь сайта = %.6f км^2, N = %d\n', ...
        R_indoor_km*1000, S_indoor, N_indoor);

%% Локальная функция: находит расстояние пересечения с заданным MAPL
function r = findRadius(d, PL, MAPL)
    idx = find(PL >= MAPL, 1, 'first');
    if isempty(idx)
        r = NaN;
        warning('PL не достиг MAPL в заданном диапазоне расстояний.');
    elseif idx == 1
        r = d(1);
        warning('Пересечение находится ближе минимального диапазона.');
    else
        % Линейная интерполяция между соседними точками.
        r = interp1(PL(idx-1:idx), d(idx-1:idx), MAPL, 'linear');
    end
end

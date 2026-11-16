#include <iostream>
#include <vector>
#include <iomanip>
#include <map>
#include <cmath>

using namespace std;

// Генерация последовательности Голда по схеме рис. 4.5 (нечётный вариант)
vector<int> generate_gold(int x_init[5], int y_init[5]) {
    int x[5], y[5];
    for (int i = 0; i < 5; i++) {
        x[i] = x_init[i];
        y[i] = y_init[i];
    }

    vector<int> gold(31);

    for (int i = 0; i < 31; i++) {
        // Выход = x5 XOR y5
        gold[i] = x[4] ^ y[4];

        // Обратные связи по рис. 4.5:
        // Верхний: x4, x5
        // Нижний:  y2, y5
        int new_x = x[3] ^ x[4];
        int new_y = y[1] ^ y[4];

        // Сдвиг вправо
        for (int j = 4; j > 0; j--) x[j] = x[j - 1];
        x[0] = new_x;

        for (int j = 4; j > 0; j--) y[j] = y[j - 1];
        y[0] = new_y;
    }
    return gold;
}

vector<int> generate_gold_127(int x_init[7], int y_init[7]) {
    int x[7], y[7];
    for (int i = 0; i < 7; i++) {
        x[i] = x_init[i];
        y[i] = y_init[i];
    }

    vector<int> gold(127);
    for (int i = 0; i < 127; i++) {
        gold[i] = x[6] ^ y[6]; 

        // Предпочтительная пара для n=7:
        // x: отводы 3 и 7
        // y: отводы 1, 2, 3 и 7
        int new_x = x[2] ^ x[6];
        int new_y = y[0] ^ y[1] ^ y[2] ^ y[6];

        for (int j = 6; j > 0; j--) x[j] = x[j - 1];
        x[0] = new_x;

        for (int j = 6; j > 0; j--) y[j] = y[j - 1];
        y[0] = new_y;
    }
    return gold;
}

// Печать последовательности
void print_seq(const vector<int>& seq, const string& name) {
    cout << name << ":\n";
    for (int b : seq) cout << b;
    cout << "\n\n";
}

bool check_pn_properties(const vector<int>& seq) {
    int N = seq.size();
    int ones = 0, zeros = 0;

    // Сбалансированность
    for (int b : seq) {
        if (b == 1) ones++;
        else zeros++;
    }

    cout << "\nПроверка свойств псевдослучайности\n";
    cout << "Длина последовательности: " << N << "\n";
    cout << "Количество единиц: " << ones << "\n";
    cout << "Количество нулей:  " << zeros << "\n";

    bool balance_ok = (abs(ones - zeros) <= 1);
    cout << "Сбалансированность: " << (balance_ok ? "выполнена" : "не выполнена") << "\n";

    // Свойство циклов
    vector<int> run_lengths;
    int current = seq[0];
    int length = 1;

    for (int i = 1; i < N; i++) {
        if (seq[i] == current) {
            length++;
        } else {
            run_lengths.push_back(length);
            current = seq[i];
            length = 1;
        }
    }
    run_lengths.push_back(length);

    map<int, int> count;
    for (int len : run_lengths) {
        count[len]++;
    }

    cout << "\nРаспределение длин циклов:\n";
    cout << "Длина | Количество\n";
    cout << "------|-----------\n";
    for (auto& p : count) {
        cout << setw(5) << p.first << " | " << p.second << "\n";
    }

    cout << "\nВсего циклов: " << run_lengths.size() << "\n";

    bool runs_ok = false;
    if (count.count(1)) {
        double ratio = (double)count[1] / run_lengths.size();
        runs_ok = (ratio >= 0.35);
    }

    cout << "Свойство циклов: " << (runs_ok ? "в целом выполняется" : "не выполняется") << "\n";

    bool result = balance_ok && runs_ok;

    cout << "ИТОГ: последовательность соответствует свойствам псевдослучайной: " << (result ? "ДА" : "НЕТ")
         << "\n";

    return result;
}

int main() {
    // Исходные данные (номер 12)
    // x = 12 : 01100
    // y = 19 : 10011
    int x1[5] = {0, 1, 1, 0, 0};
    int y1[5] = {1, 0, 0, 1, 1};

    // Новые данные (пункт 3)
    // x = 13 : 01101
    // y = 14 : 01110
    int x2[5] = {0, 1, 1, 0, 1};
    int y2[5] = {0, 1, 1, 1, 0};
    
    int x3[7] = {0, 0, 0, 1, 1, 0, 0};
    int y3[7] = {1, 0, 0, 0, 0, 0, 0};

    // Генерация последовательностей
    vector<int> seq1 = generate_gold(x1, y1);  // исходная
    vector<int> seq2 = generate_gold(x2, y2);  // новая

    vector<int> seq3 = generate_gold_127(x3, y3);

    // Пункт 1: вывод исходной последовательности
    print_seq(seq1, "1. Исходная последовательность Голда (x=12, y=19)");

    // Пункт 2: автокорреляция
    cout << "2. Автокорреляция исходной последовательности:\n";
    cout << "Сдвиг | Последовательность после сдвига              | Автокорреляция\n";
    cout << "------|-----------------------------------------------|---------------\n";

    for (int s = 0; s < 31; s++) {
        int agree = 0, disagree = 0;
        for (int i = 0; i < 31; i++) {
            if (seq1[i] == seq1[(i + s) % 31]) agree++;
            else disagree++;
        }
        double R = (agree - disagree) / 31.0;

        cout << setw(5) << s << " | ";
        for (int i = 0; i < 31; i++) cout << seq1[(i + s) % 31];
        cout << " | " << fixed << setprecision(5) << R << "\n";
    }
    cout << "\n";

    // Пункт 3: новая последовательность
    print_seq(seq2, "3. Новая последовательность Голда (x=13, y=14)");

    // Пункт 4: взаимная корреляция
    cout << "4. Взаимная корреляция исходной и новой последовательностей:\n";
    cout << "Сдвиг | Взаимная корреляция\n";
    cout << "------|--------------------\n";

    for (int s = 0; s < 31; s++) {
        int agree = 0, disagree = 0;
        for (int i = 0; i < 31; i++) {
            if (seq1[i] == seq2[(i + s) % 31]) agree++;
            else disagree++;
        }
        double R = (agree - disagree) / 31.0;
        cout << setw(5) << s << " | " << fixed << setprecision(5) << R << "\n";
    }

    check_pn_properties(seq1);

    print_seq(seq3, "\n4. Новая-новая последовательность Голда (N=127)");
    check_pn_properties(seq3);

    return 0;
}

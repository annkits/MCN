#include <iostream>
#include <vector>
#include <iomanip>

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

// Печать последовательности
void print_seq(const vector<int>& seq, const string& name) {
    cout << name << ":\n";
    for (int b : seq) cout << b;
    cout << "\n\n";
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

    // Генерация последовательностей
    vector<int> seq1 = generate_gold(x1, y1);  // исходная
    vector<int> seq2 = generate_gold(x2, y2);  // новая

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

    return 0;
}
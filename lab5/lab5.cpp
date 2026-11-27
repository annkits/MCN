#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>

using namespace std;

vector<int> generateData(int N) {
    vector<int> data(N);

    for (int i = 0; i < N; i++) {
        data[i] = rand() % 2;
    }

    return data;
}

void printBits(const vector<int>& bits) {
    for (int bit : bits) {
        cout << bit;
    }
    cout << endl;
}

vector<int> module2Division(vector<int> data, const vector<int>& G) {
    int n = data.size();
    int m = G.size();

    for (int i = 0; i <= n - m; i++) {
        if (data[i] == 1) {
            for (int j = 0; j < m; j++) {
                data[i + j] ^= G[j];
            }
        }
    }

    return vector<int>(data.end() - (m - 1), data.end());
}

vector<int> calculateCRC(vector<int> data, const vector<int>& G) {
    int crcLength = G.size() - 1;
    data.resize(data.size() + crcLength, 0);
    return module2Division(data, G);
}

bool checkError(const vector<int>& packet, const vector<int>& G) {
    vector<int> remainder = module2Division(packet, G);

    for (int bit : remainder) {
        if (bit != 0) {
            return true;
        }
    }

    return false;
}

vector<int> runExperiment(int N, const vector<int>& G) {
    cout << "\n=== N = " << N << " === " << endl;

    vector<int> data = generateData(N);
    vector<int> crc = calculateCRC(data, G);

    vector<int> packet = data;

    packet.insert(packet.end(), crc.begin(), crc.end());

    cout << "Original data: "; printBits(data);
    cout << "CRC: "; printBits(crc);
    cout << "Transmitted packet: "; printBits(packet);

    cout << "Receiver remainder: "; printBits(module2Division(packet, G));
    cout << (checkError(packet, G) ? "Error detected" : "No errors detected") << endl;

    vector<int> damagedPacket = packet;
    damagedPacket[5] ^= 1;

    cout << "\nDamaged packet: "; printBits(damagedPacket);
    cout << "Receiver remainder: "; printBits(module2Division(damagedPacket, G));
    cout << (checkError(damagedPacket, G) ? "Error detected" : "No errors detected") << endl;

    return packet;
}

void testErrors(const vector<int>& packet, const vector<int>& G) {
    int detected = 0;
    int undetected = 0;

    vector<int> damagedPacket = packet;
    cout << "\n=== Error Detection Test ===" << endl;
    cout << "Transmitted packet: "; printBits(packet);

    for (int i = 0; i < packet.size(); i++) {
        damagedPacket[i] ^= 1;
        vector<int> remainder = module2Division(damagedPacket, G);
        bool error = checkError(damagedPacket, G);

        if (error) {
            detected++;
        } else {
            undetected++;
            cout << "Undetected error at position " << i << endl;
        }
    }

    cout << "Damaged packet: "; printBits(damagedPacket);

    cout << "\nTotal: " << packet.size() << endl;
    cout << "Detected: " << detected << endl;
    cout << "Undetected: " << undetected << endl;

    cout << "Efficiency: " << 100.0 * detected / packet.size() << "%" << endl;
}

int main() {
    srand(time(nullptr));

    vector<int> G = {1, 1, 0, 1, 1, 1, 1, 0};

    runExperiment(32, G);

    vector<int> packet = runExperiment(250, G);

    testErrors(packet, G);

    return 0;
}

#include <iostream>
#include <fstream>
#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct Record {
    int id;
    std::string name;
    int value;
    std::string timestamp;
};

void merge(std::vector<Record>& records, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;

    std::vector<Record> L(n1), R(n2);

    for (int i = 0; i < n1; ++i)
        L[i] = records[left + i];
    for (int j = 0; j < n2; ++j)
        R[j] = records[mid + 1 + j];

    int i = 0, j = 0, k = left;

    while (i < n1 && j < n2) {
        if (L[i].value >= R[j].value) {
            records[k] = L[i];
            ++i;
        } else {
            records[k] = R[j];
            ++j;
        }
        ++k;
    }

    while (i < n1) {
        records[k] = L[i];
        ++i;
        ++k;
    }

    while (j < n2) {
        records[k] = R[j];
        ++j;
        ++k;
    }
}

void mergeSort(std::vector<Record>& records, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;

        mergeSort(records, left, mid);
        mergeSort(records, mid + 1, right);

        merge(records, left, mid, right);
    }
}

int main() {
    std::ifstream inputFile("data.json");
    if (!inputFile.is_open()) {
        std::cerr << "Error: Could not open data.json" << std::endl;
        return 1;
    }

    json inputData;
    inputFile >> inputData;

    std::vector<Record> records;
    for (const auto& item : inputData) {
        records.push_back({item["id"], item["name"], item["value"], item["timestamp"]});
    }

    mergeSort(records, 0, records.size() - 1);

    json outputData;
    for (const auto& record : records) {
        outputData.push_back({
            {"id", record.id},
            {"name", record.name},
            {"value", record.value},
            {"timestamp", record.timestamp}
        });
    }

    std::ofstream outputFile("sorted_data.json");
    if (!outputFile.is_open()) {
        std::cerr << "Error: Could not write sorted_data.json" << std::endl;
        return 1;
    }
    outputFile << outputData.dump(4);
    return 0;
}

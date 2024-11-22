#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <ctime>
#include <iomanip>
#include <sstream>
#include <chrono>              
#include "nlohmann/json.hpp"

#ifdef _WIN32
    #include <windows.h>
#endif

using json = nlohmann::json;

struct Record {
    int id;
    std::string name;
    int value;
    std::string timestamp;
};

std::ofstream log_file;

std::string get_current_timestamp() {
    using namespace std::chrono;

    auto now = system_clock::now();
    auto in_time_t = system_clock::to_time_t(now);
    auto ms = duration_cast<milliseconds>(now.time_since_epoch()) % 1000;

    std::tm buf;
    #ifdef _WIN32
        localtime_s(&buf, &in_time_t);
    #else
        localtime_r(&in_time_t, &buf);
    #endif

    std::ostringstream oss;
    oss << std::put_time(&buf, "%Y-%m-%d %H:%M:%S");
    oss << "," << std::setw(3) << std::setfill('0') << ms.count();
    return oss.str();
}

void log_info(const std::string& message) {
    std::string timestamp = get_current_timestamp();
    std::string log_message = timestamp + " INFO: " + message;
    std::cout << log_message << std::endl;
    if (log_file.is_open()) {
        log_file << log_message << std::endl;
    }
}

void log_error(const std::string& message) {
    std::string timestamp = get_current_timestamp();
    std::string log_message = timestamp + " ERROR: " + message;
    std::cerr << log_message << std::endl;
    if (log_file.is_open()) {
        log_file << log_message << std::endl;
    }
}

std::vector<Record> load_data(const std::string& filename) {
    std::vector<Record> records;
    std::ifstream infile(filename);
    if (!infile.is_open()) {
        log_error("Не удалось открыть файл " + filename + " для чтения.");
        return records;
    }

    json j;
    try {
        infile >> j;
    } catch (json::parse_error& e) {
        log_error("Ошибка разбора JSON: " + std::string(e.what()));
        return records;
    }

    for (const auto& item : j) {
        try {
            Record record;
            record.id = item.at("id").get<int>();
            record.name = item.at("name").get<std::string>();
            record.value = item.at("value").get<int>();
            record.timestamp = item.at("timestamp").get<std::string>();
            records.push_back(record);
        } catch (json::type_error& e) {
            log_error("Ошибка типов в JSON объекте: " + std::string(e.what()));
        } catch (json::out_of_range& e) {
            log_error("Отсутствует обязательное поле в JSON объекте: " + std::string(e.what()));
        }
    }

    log_info("Загружено " + std::to_string(records.size()) + " записей из " + filename + ".");
    return records;
}

bool save_data(const std::string& filename, const std::vector<Record>& records) {
    json j = json::array();
    for (const auto& record : records) {
        json item;
        item["id"] = record.id;
        item["name"] = record.name;
        item["value"] = record.value;
        item["timestamp"] = record.timestamp;
        j.push_back(item);
    }

    std::ofstream outfile(filename);
    if (!outfile.is_open()) {
        log_error("Не удалось открыть файл " + filename + " для записи.");
        return false;
    }

    try {
        outfile << j.dump(4);
    } catch (json::type_error& e) {
        log_error("Ошибка при сериализации JSON: " + std::string(e.what()));
        return false;
    }

    log_info("Отсортированные данные сохранены в " + filename + ".");
    return true;
}

int partition(std::vector<Record>& arr, int low, int high) {
    int pivot = arr[high].value;
    int i = low - 1;

    for(int j = low; j < high; j++) {
        if(arr[j].value >= pivot) { 
            i++;
            std::swap(arr[i], arr[j]);
        }
    }
    std::swap(arr[i + 1], arr[high]);
    return (i + 1);
}

void quick_sort(std::vector<Record>& arr, int low, int high) {
    if(low < high) {
        int pi = partition(arr, low, high);
        quick_sort(arr, low, pi - 1);
        quick_sort(arr, pi + 1, high);
    }
}

int main() {
    #ifdef _WIN32
        SetConsoleOutputCP(CP_UTF8);
    #endif

    std::string log_file_path = "../logs/app.log";
    log_file.open(log_file_path, std::ios::app);
    if (!log_file.is_open()) {
        std::cerr << "Не удалось открыть файл " << log_file_path << " для записи логов." << std::endl;
    } else {
        log_info("Начало работы программы сортировки.");
    }

    std::string input_file = "../data/data.json";
    std::string output_file = "../data/sorted_data.json";

    log_info("Чтение данных из " + input_file + "...");
    std::vector<Record> records = load_data(input_file);
    if (records.empty()) {
        log_error("Нет данных для сортировки.");
        if (log_file.is_open()) {
            log_file.close();
        }
        return 1;
    }

    log_info("Сортировка данных по полю 'value' в порядке убывания...");
    quick_sort(records, 0, records.size() - 1);
    log_info("Сортировка завершена.");

    log_info("Запись отсортированных данных в " + output_file + "...");
    if (!save_data(output_file, records)) {
        log_error("Ошибка при сохранении отсортированных данных.");
        if (log_file.is_open()) {
            log_file.close();
        }
        return 1;
    }

    log_info("Сортировка завершена успешно.");

    if (log_file.is_open()) {
        log_file.close();
    }

    return 0;
}

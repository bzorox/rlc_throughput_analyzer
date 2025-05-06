import pandas as pd
import re
from pathlib import Path
from collections import defaultdict

def parse_rlc_logs(file_path):
    """Парсит RLC логи из файла и возвращает структурированные данные."""
    log_pattern = re.compile(
        r'\[RLC\]\[(UL|DL)\]\[UE_ID=(\d+)\]\[RB_ID=\d+\]\[SN=\d+\]\s*(?:TX|RX)\s*(?:AMD|UMD)\s*PDU.*Size=(\d+)\s*bytes.*@\s*T=([\d.]+)s'
    )
    logs = []
    
    with open(file_path, 'r') as file:
        for line in file:
            match = log_pattern.search(line)
            if match:
                direction, ue_id, size, time = match.groups()
                logs.append({
                    'direction': direction,
                    'ue_id': int(ue_id),
                    'size': int(size),
                    'time': float(time)
                })
    
    return pd.DataFrame(logs)

def calculate_throughput(logs_df):
    """Вычисляет UL и DL throughput для каждого UE."""
    throughput_results = defaultdict(dict)
    
    for ue_id in logs_df['ue_id'].unique():
        ue_logs = logs_df[logs_df['ue_id'] == ue_id]
        
        # Calculate UL throughput
        ul_logs = ue_logs[ue_logs['direction'] == 'UL']
        if not ul_logs.empty:
            ul_total_bits = ul_logs['size'].sum() * 8
            ul_time = ul_logs['time'].max() - ul_logs['time'].min()
            ul_throughput = ul_total_bits / ul_time if ul_time > 0 else 0
            throughput_results[ue_id]['UL'] = ul_throughput / 1000  # в кбит/с
        
        # Calculate DL throughput
        dl_logs = ue_logs[ue_logs['direction'] == 'DL']
        if not dl_logs.empty:
            dl_total_bits = dl_logs['size'].sum() * 8
            dl_time = dl_logs['time'].max() - dl_logs['time'].min()
            dl_throughput = dl_total_bits / dl_time if dl_time > 0 else 0
            throughput_results[ue_id]['DL'] = dl_throughput / 1000  # в кбит/с
    
    return throughput_results

def main():
    print("=== RLC Log Throughput Analyzer ===")
    
    # Запрос пути к файлу
    while True:
        file_path = input("Введите путь к файлу с RLC логами: ").strip()
        if Path(file_path).is_file():
            break
        print("Файл не найден. Попробуйте снова.")
    
    # Парсинг и расчет
    try:
        print("\nОбработка логов...")
        logs_df = parse_rlc_logs(file_path)
        
        if logs_df.empty:
            print("Не найдено подходящих RLC логов в файле.")
            return
        
        throughput_results = calculate_throughput(logs_df)
        
        # Вывод результатов
        print("\nРезультаты:")
        print("{:<10} {:<15} {:<15}".format("UE ID", "UL Throughput kb/s", "DL Throughput kb/s"))
        print("-" * 40)
        for ue_id, metrics in throughput_results.items():
            ul = metrics.get('UL', 0)
            dl = metrics.get('DL', 0)
            print("{:<10} {:<15.2f} {:<15.2f}".format(ue_id, ul, dl))
        
        print("\nГотово!")
    
    except Exception as e:
        print(f"\nОшибка при обработке файла: {e}")

if __name__ == "__main__":
    main()
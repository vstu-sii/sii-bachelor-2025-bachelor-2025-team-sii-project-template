#!/usr/bin/env python3
"""
Скрипт для запуска нагрузочного тестирования
"""
import subprocess
import time
import json
import sys
from datetime import datetime
from pathlib import Path

def run_locust_test(
    users: int = 10,
    spawn_rate: int = 1,
    run_time: str = "1m",
    host: str = "http://localhost:8000"
):
    """Запуск теста с помощью Locust"""
    
    reports_dir = Path(__file__).parent.parent / "reports" / "load_tests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"load_test_{timestamp}.html"
    csv_prefix = reports_dir / f"load_test_{timestamp}"
    
    cmd = [
        "locust",
        "-f", str(Path(__file__).parent / "locustfile.py"),
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--headless",
        "--html", str(report_file),
        "--csv", str(csv_prefix),
        "--loglevel", "INFO"
    ]
    
    print(f"Starting load test with {users} users...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Анализ результатов
        analyze_results(csv_prefix)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running load test: {e}")
        return False

def analyze_results(csv_prefix: Path):
    """Анализ результатов нагрузочного тестирования"""
    
    stats_file = csv_prefix.with_suffix('.csv')
    
    if not stats_file.exists():
        print("Stats file not found")
        return
    
    import pandas as pd
    
    try:
        df = pd.read_csv(stats_file)
        
        print("\n" + "="*50)
        print("АНАЛИЗ РЕЗУЛЬТАТОВ НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")
        print("="*50)
        
        # Основные метрики
        total_requests = df['Request Count'].sum()
        failure_rate = (df['Failure Count'].sum() / total_requests * 100) if total_requests > 0 else 0
        
        print(f"Всего запросов: {total_requests}")
        print(f"Процент ошибок: {failure_rate:.2f}%")
        
        # Latency анализ
        for _, row in df.iterrows():
            if row['Name'] != 'Total':
                print(f"\n{row['Name']}:")
                print(f"  Avg Response Time: {row['Average Response Time']:.2f}ms")
                print(f"  Min Response Time: {row['Min Response Time']:.2f}ms")
                print(f"  Max Response Time: {row['Max Response Time']:.2f}ms")
                print(f"  Requests/s: {row['Requests/s']:.2f}")
        
        # Генерация отчета
        generate_load_report(df, csv_prefix)
        
    except Exception as e:
        print(f"Error analyzing results: {e}")

def generate_load_report(df, csv_prefix: Path):
    """Генерация детального отчета"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_requests": int(df['Request Count'].sum()),
            "total_failures": int(df['Failure Count'].sum()),
            "failure_rate": float(df['Failure Count'].sum() / df['Request Count'].sum() * 100) if df['Request Count'].sum() > 0 else 0,
            "avg_rps": float(df['Requests/s'].mean())
        },
        "endpoints": []
    }
    
    for _, row in df.iterrows():
        if row['Name'] != 'Total':
            report["endpoints"].append({
                "name": row['Name'],
                "requests": int(row['Request Count']),
                "failures": int(row['Failure Count']),
                "avg_response_time": float(row['Average Response Time']),
                "min_response_time": float(row['Min Response Time']),
                "max_response_time": float(row['Max Response Time']),
                "median_response_time": float(row['Median Response Time']),
                "rps": float(row['Requests/s'])
            })
    
    # Сохраняем JSON отчет
    json_report = csv_prefix.with_suffix('.json')
    with open(json_report, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nДетальный отчет сохранен: {json_report}")

def run_scenario_tests():
    """Запуск различных сценариев тестирования"""
    
    scenarios = [
        {"name": "Низкая нагрузка", "users": 5, "spawn_rate": 1, "duration": "30s"},
        {"name": "Средняя нагрузка", "users": 20, "spawn_rate": 2, "duration": "1m"},
        {"name": "Высокая нагрузка", "users": 50, "spawn_rate": 5, "duration": "2m"},
        {"name": "Пиковая нагрузка", "users": 100, "spawn_rate": 10, "duration": "30s"},
        {"name": "Продолжительная", "users": 10, "spawn_rate": 1, "duration": "5m"},
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"Сценарий: {scenario['name']}")
        print(f"Пользователи: {scenario['users']}, Длительность: {scenario['duration']}")
        print('='*60)
        
        start_time = time.time()
        success = run_locust_test(
            users=scenario['users'],
            spawn_rate=scenario['spawn_rate'],
            run_time=scenario['duration']
        )
        elapsed = time.time() - start_time
        
        results.append({
            **scenario,
            "success": success,
            "elapsed_seconds": elapsed
        })
    
    # Сводный отчет по сценариям
    print("\n" + "="*60)
    print("СВОДКА ПО СЦЕНАРИЯМ")
    print("="*60)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['name']}: {result['users']} users, {result['duration']}, "
              f"time: {result['elapsed_seconds']:.1f}s")

if __name__ == "__main__":
    # Парсинг аргументов командной строки
    import argparse
    
    parser = argparse.ArgumentParser(description="Нагрузочное тестирование API")
    parser.add_argument("--users", type=int, default=10, help="Количество пользователей")
    parser.add_argument("--spawn-rate", type=int, default=1, help="Скорость появления пользователей")
    parser.add_argument("--duration", type=str, default="1m", help="Длительность теста")
    parser.add_argument("--host", type=str, default="http://localhost:8000", help="Хост API")
    parser.add_argument("--scenario", action="store_true", help="Запустить все сценарии")
    
    args = parser.parse_args()
    
    if args.scenario:
        run_scenario_tests()
    else:
        run_locust_test(
            users=args.users,
            spawn_rate=args.spawn_rate,
            run_time=args.duration,
            host=args.host
        )
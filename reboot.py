import subprocess
import ipaddress
import argparse
import concurrent.futures
import sys

def reboot_device(ip):
    """Отправляет запрос на перезагрузку устройства по IP"""
    curl_cmd = [
        'curl',
        '--digest',
        '-u', 'root:root',
        '-X', 'GET',
        '-H', 'Content-Type: application/json',
        f'http://{ip}/cgi-bin/reboot.cgi'
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"Успешная перезагрузка {ip}")
        else:
            print(f"Ошибка при перезагрузке {ip}: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"Таймаут при перезагрузке {ip}")
    except Exception as e:
        print(f"Ошибка при перезагрузке {ip}: {str(e)}")

def get_ip_list(subnet):
    """Возвращает список IP-адресов в подсети"""
    try:
        network = ipaddress.ip_network(subnet, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"Ошибка в формате подсети: {str(e)}")
        sys.exit(1)

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Перезагрузка устройств в подсети')
    parser.add_argument('subnet', help='Подсеть в формате CIDR (например, 172.16.50.0/24)')
    parser.add_argument('--max-workers', type=int, default=10, 
                       help='Максимальное количество одновременных подключений (по умолчанию: 10)')
    
    args = parser.parse_args()

    # Получение списка IP-адресов
    ip_list = get_ip_list(args.subnet)
    
    print(f"Найдено {len(ip_list)} IP-адресов для перезагрузки")
    
    # Параллельная перезагрузка устройств
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        executor.map(reboot_device, ip_list)

if __name__ == "__main__":
    main()
import argparse
import datetime as dt
import json
from tabulate import tabulate
import sys


DATE_FORMAT = '%Y-%m-%d'


class ReportStrategy():
    '''Абстрактный базовый класс для стратегий отчета'''

    def __init__(self):
        pass

    def process_record(self, record: dict):
        pass

    def generate_report(self):
        pass


class AverageReport(ReportStrategy):
    '''Отчет по среднему времени ответа для эндпоинтов'''

    def __init__(self):
        self.stats = {}
        self.headers = ('handler', 'total', 'avg_response_time')

    def process_record(self, record: dict):
        endpoint = record.get('url')
        self.stats.setdefault(
            endpoint,
            {
                'total': 0,
                'sum_response_time': 0
            }
        )
        self.stats[endpoint]['total'] += 1
        self.stats[endpoint]['sum_response_time'] += record.get(
            'response_time'
        )

    def generate_report(self):
        table = []
        sorted_items = sorted(
            self.stats.items(),
            key=lambda total_requests: total_requests[1]['total'],
            reverse=True
        )

        for idx, (endpoint, data) in enumerate(sorted_items):
            avg_time = data['sum_response_time'] / data['total']
            table.append([
                idx,
                endpoint,
                data['total'],
                round(avg_time, 3)
            ])
        return table


class UserAgentReport(ReportStrategy):
    '''Отчет по популярности браузеров на основе User-Agent'''

    def __init__(self):
        pass

    def process_record(self, record):
        pass

    def generate_report(self):
        pass


def parse_arguments():
    '''Парсинг аргументов командной строки'''

    parser = argparse.ArgumentParser(
        description='Анализ логов веб-сервера и создание отчетов',
        epilog='Примеры использования:\n'
        '\n\tpython3 main.py -f example0.log -r average\n'
        '\n\tpython main.py --file examples/*.log --report user_agent'
        ' --date 2025-22-06',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-f', '--file',
        nargs='+',
        type=argparse.FileType(),
        required=True,
        help='Путь до файла(файлов) с логами (JSON объектами),'
        ' открыт в режиме чтения'
    )

    parser.add_argument(
        '-r', '--report',
        type=str,
        # Есть возможность добавить другие типы отчета (e.g. User-Agent)
        choices=['average', 'user_agent'],
        required=True,
        help='Тип создаваемого отчета (доступны: \'average\', \'user_agent\')'
    )

    parser.add_argument(
        '-d', '--date',
        type=str,
        # В задании пример указан в формате ГГГГ-ДД-ММ, а в логах ГГГГ-ММ-ДД,
        # я ориентировался на ЛОГИ.
        help='Фильтрация логов по дате в формате ГГГГ-ММ-ДД'
    )

    return parser.parse_args()


def filter_by_date(record, target_date=None):
    '''Сравнение указанной даты(если дата указана) с датой из записи лога'''
    if target_date:
        try:
            date = dt.datetime.strptime(
                record.get('@timestamp').split('T')[0],
                DATE_FORMAT
            ).date()
        except ValueError:
            return False
        return target_date == date
    return True


def load_data(file_paths, strategy: ReportStrategy, target_date=None):
    '''Загружает и обрабатывает логи из файла(файлов)'''
    for file_path in file_paths:
        try:
            with open(file_path) as file:
                for line in file:
                    try:
                        record = json.loads(line)

                        if not filter_by_date(record, target_date):
                            continue

                        strategy.process_record(record)

                    except json.JSONDecodeError as e:
                        print(
                            f'Некорректный JSON-объект: {e}',
                            file=sys.stderr
                        )
        except Exception as e:
            print(f'Ошибка при обработке {file_path}: {e}', file=sys.stderr)


def get_strategy(report_type):
    '''Создание объекта класса в зависимости от типа отчета'''
    match report_type:
        case 'average':
            return AverageReport()
        # Есть возможность добавить другие типы отчета
        case 'user_agent':
            return UserAgentReport()
        case _:
            raise ValueError(f'Неизвестный тип отчета: {report_type}!!!')


def parse_date(date_str):
    '''Парсит дату из строки в объект date'''
    try:
        return dt.datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError:
        raise ValueError('Неверный формат даты! Используйте ГГГГ-ММ-ДД')


def main():
    args = parse_arguments()

    file_paths = [file_path.name for file_path in args.file]

    report_strategy = get_strategy(args.report)

    target_date = parse_date(args.date) if args.date else None

    load_data(file_paths, report_strategy, target_date)

    print(tabulate(report_strategy.generate_report(),
                   headers=report_strategy.headers))


if __name__ == "__main__":
    main()

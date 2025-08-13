 ```python
 """
 Тесты для скрипта анализа лог-файлов.
 """
 ```
import datetime as dt
import json

import pytest

from main import (AverageReport, UserAgentReport, filter_by_date, get_strategy,
                  load_data, main, parse_date)


@pytest.mark.parametrize(
    'date, result',
    [
        ('2025-06-22', dt.date(2025, 6, 22)),
        ('2020-07-31', dt.date(2020, 7, 31)),
        ('2023-01-01', dt.date(2023, 1, 1))
    ]
)
def test_parse_date_successed(date, result):
    '''Проверяет корректный парсинг валидных дат.'''
    assert parse_date(date) == result


@pytest.mark.parametrize(
    'date, result',
    [
        ('2025-06-31', ValueError),
        ('2025-22-06', ValueError),
        ('sdhfkshdjfksdhkj', ValueError)
    ]
)
def test_parse_date_failed(date, result):
    '''Проверяет обработку невалидных форматов даты.'''
    with pytest.raises(ValueError):
        parse_date(date)


@pytest.mark.parametrize(
    'report_type, result',
    [
        ('average', AverageReport),
        ('user_agent', UserAgentReport)
    ]
    )
def test_get_strategy_successed(report_type, result):
    '''Проверяет создание объектов стратегий для валидных типов отчетов.'''
    assert isinstance(get_strategy(report_type), result)


@pytest.mark.parametrize(
    'report_type, result',
    [
        ('status', ValueError),
        ('Average', ValueError),
        ('fhgjdfhkgh', ValueError)
    ]
)
def test_get_strategy_failed(report_type, result):
    '''Проверяет обработку невалидных типов отчетов.'''
    with pytest.raises(ValueError):
        get_strategy(report_type)


@pytest.fixture
def average_report_data():
    sample_log_lines = [
        {
            "@timestamp": "2025-06-22T13:57:32+00:00",
            "status": 200,
            "url": "/api/context/...",
            "request_method": "GET",
            "response_time": 0.024,
            "http_user_agent": "..."
        },
        {
            "@timestamp": "2025-06-22T13:57:32+00:00",
            "status": 200,
            "url": "/api/context/...",
            "request_method": "GET",
            "response_time": 0.02,
            "http_user_agent": "..."
        },
        {
            "@timestamp": "2025-06-22T13:57:32+00:00",
            "status": 200,
            "url": "/api/homeworks/...",
            "request_method": "GET",
            "response_time": 0.06,
            "http_user_agent": "..."
        }
    ]
    report = AverageReport()
    for line in sample_log_lines:
        report.process_record(line)
    return report


def test_average_report_procecc_record(average_report_data):
    '''Проверяет корректность обработки записей и расчета статистики.'''
    assert average_report_data.stats["/api/context/..."]["total"] == 2
    assert average_report_data.stats[
        "/api/context/..."]["sum_response_time"] == 0.044
    assert average_report_data.stats["/api/homeworks/..."]["total"] == 1
    assert average_report_data.stats[
        "/api/homeworks/..."]["sum_response_time"] == 0.06


def test_average_report_generate_report(average_report_data):
    '''Проверяет формат и данные итогового отчета.'''
    assert average_report_data.generate_report() == [
        [0, "/api/context/...", 2, pytest.approx(0.022)],
        [1, "/api/homeworks/...", 1, pytest.approx(0.06)]
    ]


@pytest.fixture
def filter_date_record_true():
    return {
            "@timestamp": "2025-06-22T13:57:32+00:00",
            "status": 200,
            "url": "/api/context/...",
            "request_method": "GET",
            "response_time": 0.024,
            "http_user_agent": "..."
        }


def test_filter_by_date_true(filter_date_record_true):
    '''Проверяет совпадение даты записи с указанной датой.'''
    assert filter_by_date(
        filter_date_record_true,
        dt.date(2025, 6, 22)) is True


def test_filter_without_date(filter_date_record_true):
    '''Проверяет обработку записей при отсутствии фильтрации по дате.'''
    assert filter_by_date(filter_date_record_true, None) is True


def test_filter_by_date_false(filter_date_record_true):
    '''Проверяет несовпадение даты записи с целевой датой.'''
    assert filter_by_date(
        filter_date_record_true,
        dt.date(2025, 7, 12)) is False


@pytest.fixture
def filter_date_records_failed():
    return [
        {
            "@timestamp": "2025-33-12T13:57:32+00:00",
            "status": 200,
            "url": "/api/context/...",
            "request_method": "GET",
            "response_time": 0.02,
            "http_user_agent": "..."
        },
        {
            "@timestamp": "2025.06.22T13:57:32+00:00",
            "status": 200,
            "url": "/api/homeworks/...",
            "request_method": "GET",
            "response_time": 0.06,
            "http_user_agent": "..."
        },
        {
            "@timestamp": "22-06-2025T13:57:32+00:00",
            "status": 200,
            "url": "/api/homeworks/...",
            "request_method": "GET",
            "response_time": 0.06,
            "http_user_agent": "..."
        }
    ]


def test_filter_by_date_failed(filter_date_records_failed):
    '''Проверяет обработку записей с невалидными форматами даты.'''
    for record in filter_date_records_failed:
        assert filter_by_date(record, dt.date(2025, 6, 22)) is False


@pytest.fixture
def sample_log_file(tmp_path):
    data = [
        {
            "@timestamp": "2025-06-22T13:57:34+00:00",
            "status": 200,
            "url": "/api/specializations/...",
            "request_method": "GET",
            "response_time": 0.044,
            "http_user_agent": "..."
        },
        {
            "@timestamp": "2025-06-22T13:57:34+00:00",
            "status": 200,
            "url": "/api/homeworks/...",
            "request_method": "GET",
            "response_time": 0.04,
            "http_user_agent": "..."
        },
        {
            "@timestamp": "2025-06-23T13:57:34+00:00",
            "status": 200,
            "url": "/api/challenges/...",
            "request_method": "GET",
            "response_time": 0.056,
            "http_user_agent": "..."
        },
        {
            "@timestamp": "2025-07-12T13:57:34+00:00",
            "status": 200,
            "url": "/api/homeworks/...",
            "request_method": "GET",
            "response_time": 0.06,
            "http_user_agent": "..."
        },
        "{invalid: json}",
        {"missing_fields": True}
    ]
    file_path = tmp_path / 'test1.log'
    with open(file_path, 'w') as file:
        for record in data:
            if isinstance(record, dict):
                file.write(json.dumps(record) + '\n')
            else:
                file.write(record + '\n')
    return file_path


def test_load_data_without_date(sample_log_file, capsys):
    '''Проверяет загрузку данных без фильтрации по дате.'''
    strategy = AverageReport()
    load_data([sample_log_file], strategy)
    captured = capsys.readouterr()

    assert 'Некорректный JSON-объект' in captured.err
    assert 'Ошибка при обработке' in captured.err
    assert "/api/homeworks/..." in strategy.stats
    assert strategy.stats["/api/homeworks/..."]["total"] == 2
    assert strategy.stats[
        "/api/homeworks/..."]["sum_response_time"] == 0.1
    assert "/api/specializations/..." in strategy.stats
    assert strategy.stats["/api/specializations/..."]["total"] == 1
    assert "/api/challenges/..." in strategy.stats
    assert strategy.stats["/api/challenges/..."]["sum_response_time"] == 0.056


def test_load_data_with_date_filter(sample_log_file):
    '''Проверяет фильтрацию записей по указанной дате.'''
    strategy = AverageReport()

    load_data([sample_log_file], strategy, target_date=dt.date(2025, 6, 22))

    assert "/api/challenges/..." not in strategy.stats
    assert "/api/specializations/..." in strategy.stats
    assert strategy.stats["/api/homeworks/..."]["total"] == 1


def test_load_data_file_not_found(capsys, tmp_path):
    'Проверяет обработку несуществующих файлов'
    strategy = AverageReport()
    fake_file = tmp_path / "non_existent.log"

    load_data([fake_file], strategy)

    captured = capsys.readouterr()
    assert "Ошибка при обработке" in captured.err
    assert "non_existent.log" in captured.err


def test_load_data_empty_file(tmp_path, capsys):
    'Проверяет обработку пустого файла'
    empty_file = tmp_path / "empty.log"
    empty_file.touch()

    strategy = AverageReport()
    load_data([empty_file], strategy)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert strategy.stats == {}


def test_main_integration(monkeypatch, capsys, tmp_path):
    'Интеграционный тест всего скрипта'
    log_file = tmp_path / "test.log"
    with open(log_file, 'w') as f:
        f.write(json.dumps({
            "@timestamp": "2025-06-22T13:57:34+00:00",
            "status": 200,
            "url": "/api/specializations/...",
            "request_method": "GET",
            "response_time": 0.044,
            "http_user_agent": "..."
        }) + '\n')

    monkeypatch.setattr(
        'sys.argv',
        ['main.py', '--file', str(log_file), '--report', 'average']
    )

    main()

    captured = capsys.readouterr()
    assert "/api/specializations/..." in captured.out
    assert "1" in captured.out
    assert "0.044" in captured.out

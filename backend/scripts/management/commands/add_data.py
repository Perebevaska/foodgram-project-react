import csv
import os

import psycopg2
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Добавление записей в БД из файлов .csv'

    def add_arguments(self, parser):
        """Аргументы для пути к файлу .csv и имени таблицы."""
        parser.add_argument('path', type=str, help='Путь к файлу .csv')
        parser.add_argument('tab_name', type=str,
                            help='Имя таблицы postgresql')

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        table = kwargs['tab_name']
        if not os.path.isfile(path):
            raise CommandError(f'Файл "{path}" не найден')
        if not table.isidentifier():
            raise CommandError(f'Невалидное имя таблицы "{table}"')
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
        )
        with conn, conn.cursor() as cur:
            with open(path, 'r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    name, unit = row
                    cur.execute(
                        f'INSERT INTO {table} ('
                        f'name, measurement_unit) VALUES (%s, %s)',
                        (name, unit)
                    )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Записи успешно добавлены в таблицу {table}'
                )
            )

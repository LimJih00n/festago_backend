"""
CSV 파일에서 이벤트 데이터를 가져와 DB에 저장하는 명령어

사용법:
    python manage.py import_events events.csv
    python manage.py import_events events.csv --clear  # 기존 데이터 삭제 후 임포트
"""

import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from events.models import Event


class Command(BaseCommand):
    help = 'CSV 파일에서 이벤트 데이터를 가져옵니다'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV 파일 경로')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 이벤트 데이터를 모두 삭제하고 시작합니다'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear = options['clear']

        # 기존 데이터 삭제
        if clear:
            count = Event.objects.count()
            Event.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'기존 이벤트 {count}개를 삭제했습니다.')
            )

        # CSV 읽기
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                success_count = 0
                error_count = 0

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # 카테고리 검증
                        category = row['category'].strip()
                        valid_categories = ['festival', 'concert', 'exhibition', 'popup']
                        if category not in valid_categories:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'행 {row_num}: 잘못된 카테고리 "{category}". '
                                    f'가능한 값: {", ".join(valid_categories)}'
                                )
                            )
                            error_count += 1
                            continue

                        # 날짜 파싱
                        start_date = datetime.strptime(row['start_date'].strip(), '%Y-%m-%d').date()
                        end_date = datetime.strptime(row['end_date'].strip(), '%Y-%m-%d').date()

                        # 좌표 파싱 (선택사항)
                        latitude = None
                        longitude = None
                        if row.get('latitude') and row['latitude'].strip():
                            latitude = float(row['latitude'].strip())
                        if row.get('longitude') and row['longitude'].strip():
                            longitude = float(row['longitude'].strip())

                        # 이벤트 생성
                        event = Event.objects.create(
                            name=row['name'].strip(),
                            description=row['description'].strip(),
                            category=category,
                            location=row['location'].strip(),
                            address=row['address'].strip(),
                            latitude=latitude,
                            longitude=longitude,
                            start_date=start_date,
                            end_date=end_date,
                            poster_image=row['poster_image'].strip(),
                            website_url=row.get('website_url', '').strip(),
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {event.name} (행 {row_num})')
                        )
                        success_count += 1

                    except KeyError as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'행 {row_num}: 필수 컬럼 누락 - {e}'
                            )
                        )
                        error_count += 1
                    except ValueError as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'행 {row_num}: 데이터 형식 오류 - {e}'
                            )
                        )
                        error_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'행 {row_num}: {row.get("name", "알 수 없음")} - {e}'
                            )
                        )
                        error_count += 1

                # 결과 요약
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS(f'✓ 성공: {success_count}개'))
                if error_count > 0:
                    self.stdout.write(self.style.ERROR(f'✗ 실패: {error_count}개'))
                self.stdout.write(self.style.SUCCESS(f'총 {Event.objects.count()}개의 이벤트가 DB에 있습니다.'))
                self.stdout.write('='*50)

        except FileNotFoundError:
            raise CommandError(f'파일을 찾을 수 없습니다: {csv_file}')
        except Exception as e:
            raise CommandError(f'CSV 파일 읽기 실패: {e}')

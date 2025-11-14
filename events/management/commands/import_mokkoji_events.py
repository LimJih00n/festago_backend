"""
CSV/Excel 파일에서 이벤트 데이터를 가져와 DB에 저장하는 명령어
- CSV와 Excel 파일 모두 지원
- title -> name 자동 변환
- Excel 날짜 형식 자동 변환
- 중복 데이터 체크 및 제거

사용법:
    python manage.py import_mokkoji_events
    python manage.py import_mokkoji_events --clear  # 기존 데이터 삭제 후 임포트
"""

import pandas as pd
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from events.models import Event
from django.db import IntegrityError
import os


class Command(BaseCommand):
    help = 'CSV/Excel 파일에서 이벤트 데이터를 가져옵니다 (중복 제거, 날짜 변환 포함)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 이벤트 데이터를 모두 삭제하고 시작합니다'
        )
        parser.add_argument(
            '--csv',
            type=str,
            default='scripts/Mokkoji_events_1.csv',
            help='CSV 파일 경로 (기본값: scripts/Mokkoji_events_1.csv)'
        )
        parser.add_argument(
            '--excel',
            type=str,
            default='scripts/Mokkoji_events_2.xlsx',
            help='Excel 파일 경로 (기본값: scripts/Mokkoji_events_2.xlsx)'
        )

    def convert_excel_date(self, value):
        """Excel 날짜 직렬화 숫자를 날짜로 변환"""
        if pd.isna(value):
            return None

        # 이미 날짜 형식인 경우
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.date()

        # 문자열인 경우
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except:
                pass

        # Excel 숫자 형식인 경우 (1900-01-01 기준)
        try:
            excel_epoch = datetime(1899, 12, 30)
            return (excel_epoch + timedelta(days=float(value))).date()
        except:
            return None

    def clean_text(self, value):
        """텍스트 정리 (앞뒤 공백 제거, None 처리)"""
        if pd.isna(value):
            return ''
        return str(value).strip()

    def process_file(self, file_path, file_type='csv'):
        """파일을 읽고 DataFrame으로 반환"""
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.WARNING(f'파일을 찾을 수 없습니다: {file_path}')
            )
            return None

        try:
            if file_type == 'csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            else:  # excel
                df = pd.read_excel(file_path)

            self.stdout.write(
                self.style.SUCCESS(f'[OK] {file_path} 파일 읽기 성공: {len(df)}개 행')
            )
            return df
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'파일 읽기 실패 ({file_path}): {e}')
            )
            return None

    def normalize_dataframe(self, df):
        """DataFrame 정규화 (컬럼명 변환 등)"""
        # title -> name 변환
        if 'title' in df.columns:
            df = df.rename(columns={'title': 'name'})

        # BOM 제거 (CSV 파일에서 발생할 수 있음)
        df.columns = df.columns.str.replace('\ufeff', '')

        return df

    def handle(self, *args, **options):
        clear = options['clear']
        csv_file = options['csv']
        excel_file = options['excel']

        # 기존 데이터 삭제
        if clear:
            count = Event.objects.count()
            Event.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'기존 이벤트 {count}개를 삭제했습니다.')
            )

        # 데이터 로드
        dfs = []

        # CSV 파일 처리
        df_csv = self.process_file(csv_file, 'csv')
        if df_csv is not None:
            dfs.append(df_csv)

        # Excel 파일 처리
        df_excel = self.process_file(excel_file, 'excel')
        if df_excel is not None:
            dfs.append(df_excel)

        if not dfs:
            self.stdout.write(
                self.style.ERROR('읽을 수 있는 파일이 없습니다.')
            )
            return

        # 데이터 합치기
        df_combined = pd.concat(dfs, ignore_index=True)
        self.stdout.write(
            self.style.SUCCESS(f'총 {len(df_combined)}개의 행을 로드했습니다.')
        )

        # DataFrame 정규화
        df_combined = self.normalize_dataframe(df_combined)

        # 중복 제거 (name, location, start_date 기준)
        before_dedup = len(df_combined)
        df_combined = df_combined.drop_duplicates(
            subset=['name', 'location', 'start_date'],
            keep='first'
        )
        after_dedup = len(df_combined)
        removed = before_dedup - after_dedup

        if removed > 0:
            self.stdout.write(
                self.style.WARNING(f'중복 데이터 {removed}개를 제거했습니다.')
            )

        # 이벤트 생성
        success_count = 0
        error_count = 0
        skip_count = 0

        for idx, row in df_combined.iterrows():
            try:
                # 필수 필드 검증
                name = self.clean_text(row.get('name'))
                if not name:
                    skip_count += 1
                    continue

                # 카테고리 검증
                category = self.clean_text(row.get('category', 'festival')).lower()
                valid_categories = ['festival', 'concert', 'exhibition', 'popup']
                if category not in valid_categories:
                    category = 'festival'  # 기본값

                # 날짜 변환
                start_date = self.convert_excel_date(row.get('start_date'))
                end_date = self.convert_excel_date(row.get('end_date'))

                if not start_date or not end_date:
                    skip_count += 1
                    continue

                # 좌표 변환
                latitude = None
                longitude = None
                try:
                    lat_val = row.get('latitude')
                    lon_val = row.get('longitude')
                    if not pd.isna(lat_val):
                        latitude = float(lat_val)
                    if not pd.isna(lon_val):
                        longitude = float(lon_val)
                except:
                    pass

                # 중복 체크 (DB에 이미 있는지)
                existing = Event.objects.filter(
                    name=name,
                    location=self.clean_text(row.get('location')),
                    start_date=start_date
                ).first()

                if existing:
                    skip_count += 1
                    continue

                # 이벤트 생성
                event = Event.objects.create(
                    name=name,
                    description=self.clean_text(row.get('description', '')),
                    category=category,
                    location=self.clean_text(row.get('location', '')),
                    address=self.clean_text(row.get('address', '')),
                    latitude=latitude,
                    longitude=longitude,
                    start_date=start_date,
                    end_date=end_date,
                    poster_image=self.clean_text(row.get('poster_image', '')),
                    website_url=self.clean_text(row.get('website_url', '')),
                )

                # 성공 카운트만 증가 (출력 제거 - 인코딩 에러 방지)
                success_count += 1

            except IntegrityError as e:
                skip_count += 1
            except Exception as e:
                error_count += 1

        # 결과 요약
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'[OK] 성공: {success_count}개'))
        if skip_count > 0:
            self.stdout.write(self.style.WARNING(f'[SKIP] 건너뜀: {skip_count}개 (중복 또는 필수 데이터 누락)'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'[ERR] 실패: {error_count}개'))
        self.stdout.write(self.style.SUCCESS(f'총 {Event.objects.count()}개의 이벤트가 DB에 있습니다.'))
        self.stdout.write('='*60)

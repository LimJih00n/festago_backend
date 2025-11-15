#!/usr/bin/env python
"""
CSV 파일을 Django fixtures JSON으로 변환하는 스크립트

사용법:
    python scripts/csv_to_fixtures.py
"""

import csv
import json
from datetime import datetime, timedelta, timezone as dt_timezone


def excel_date_to_iso(excel_date):
    """
    Excel 날짜 시리얼 번호를 ISO 형식 날짜로 변환
    Excel은 1900년 1월 1일을 기준(1)으로 날짜를 계산
    """
    if not excel_date or excel_date == '':
        return None

    try:
        # Excel 날짜는 1900-01-01을 기준으로 함 (단, Excel의 버그로 1900-02-28 이전은 -1일 보정 필요)
        # 하지만 1900-03-01 이후는 문제 없음
        excel_date = int(float(excel_date))
        base_date = datetime(1899, 12, 30)  # Excel의 기준일 (1900-01-01 = 1)
        converted_date = base_date + timedelta(days=excel_date)
        return converted_date.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        # 이미 날짜 형식인 경우 그대로 반환
        return str(excel_date)


def csv_to_fixtures(csv_file_path, output_json_path, start_pk=1):
    """
    CSV 파일을 Django fixtures JSON으로 변환

    Args:
        csv_file_path: 입력 CSV 파일 경로
        output_json_path: 출력 JSON 파일 경로
        start_pk: 시작 Primary Key (기본값: 1)
    """
    fixtures = []

    # 현재 시간 (ISO 8601 형식, timezone-aware)
    now = datetime.now(dt_timezone.utc).isoformat()

    # CSV 파일 읽기
    with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        for idx, row in enumerate(reader, start=start_pk):
            # Django fixtures 형식으로 변환
            fixture = {
                "model": "events.Event",
                "pk": idx,
                "fields": {
                    "name": row['title'].strip(),
                    "description": row['description'].strip(),
                    "category": row['category'].strip(),
                    "location": row['location'].strip(),
                    "address": row['address'].strip(),
                    "latitude": float(row['latitude']) if row['latitude'] else None,
                    "longitude": float(row['longitude']) if row['longitude'] else None,
                    "start_date": excel_date_to_iso(row['start_date']),
                    "end_date": excel_date_to_iso(row['end_date']),
                    "poster_image": row['poster_image'].strip(),
                    "website_url": row['website_url'].strip() if row['website_url'] else "",
                    "created_at": now,
                    "updated_at": now,
                }
            }

            fixtures.append(fixture)

    # JSON 파일로 저장
    with open(output_json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(fixtures, jsonfile, ensure_ascii=False, indent=2)

    print(f"Conversion completed!")
    print(f"Input file: {csv_file_path}")
    print(f"Output file: {output_json_path}")
    print(f"Total events: {len(fixtures)}")
    print(f"PK range: {start_pk} ~ {start_pk + len(fixtures) - 1}")


if __name__ == "__main__":
    # CSV → JSON 변환
    csv_to_fixtures(
        csv_file_path='scripts/Mokkoji_events_1.csv',
        output_json_path='fixtures/mokkoji_events.json',
        start_pk=1
    )

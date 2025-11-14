import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Event

# 좌표가 있는 이벤트 확인
events_with_coords = Event.objects.filter(
    latitude__isnull=False, 
    longitude__isnull=False
).values('id', 'name', 'location', 'latitude', 'longitude', 'category')

print(f"총 이벤트 수: {Event.objects.count()}")
print(f"좌표 있는 이벤트: {events_with_coords.count()}")
print(f"\n지도에 표시될 마커 샘플 (처음 5개):\n")

for event in events_with_coords[:5]:
    print(f"[{event['category']}] {event['name']}")
    print(f"  위치: {event['location']}")
    print(f"  좌표: ({event['latitude']}, {event['longitude']})")
    print()

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Event
from events.serializers import EventSerializer

# 첫 번째 이벤트 가져오기
event = Event.objects.first()

if event:
    # Serializer로 변환
    serializer = EventSerializer(event)
    data = serializer.data
    
    print("=== Frontend 호환성 체크 ===\n")
    print("Django Model -> API Response (JSON):\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print("\n\n=== Frontend가 필요한 필드 ===")
    required_fields = ['id', 'name', 'description', 'category', 'location', 'start_date', 'end_date', 'poster_image']
    
    for field in required_fields:
        status = "OK" if field in data else "MISSING"
        value = data.get(field, "N/A")
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        print(f"  [{status}] {field}: {value}")
    
    print("\n\n=== 추가 필드 ===")
    extra_fields = [f for f in data.keys() if f not in required_fields]
    for field in extra_fields:
        value = data.get(field, "N/A")
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        print(f"  {field}: {value}")
else:
    print("No events in database")

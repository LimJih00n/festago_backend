import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Event
from django.db.models import Count

print("Total events:", Event.objects.count())
print("\nBy category:")
for item in Event.objects.values('category').annotate(count=Count('category')).order_by('category'):
    print(f"  {item['category']}: {item['count']}")

print("\nRecent 5 events:")
for event in Event.objects.all()[:5]:
    print(f"  - {event.name} ({event.category}, {event.location})")

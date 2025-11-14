import json
from datetime import datetime

# Read events.json
with open('fixtures/events.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

# Add created_at and updated_at to each event
current_time = datetime.now().isoformat()

for event in events:
    event['fields']['created_at'] = '2025-10-01T00:00:00Z'
    event['fields']['updated_at'] = '2025-10-01T00:00:00Z'

# Write back
with open('fixtures/events.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print("✅ Fixed events.json - added created_at and updated_at fields")
print(f"📊 Updated {len(events)} events")

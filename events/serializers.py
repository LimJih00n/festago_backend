from rest_framework import serializers
from .models import Event, Bookmark, Review


class EventSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_is_bookmarked(self, obj):
        """현재 로그인한 사용자가 북마크했는지 여부"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, event=obj).exists()
        return False


class EventMapSerializer(serializers.ModelSerializer):
    """지도용 간소화된 Serializer"""
    class Meta:
        model = Event
        fields = ['id', 'name', 'category', 'location', 'latitude', 'longitude', 'start_date', 'end_date']


class BookmarkSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'event', 'event_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # 현재 로그인한 사용자를 자동으로 할당
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True)
    event_id = serializers.IntegerField(write_only=True, required=False)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_name', 'event', 'event_id', 'event_name',
            'rating', 'comment', 'images', 'created_at', 'updated_at', 'is_owner'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_is_owner(self, obj):
        """현재 로그인한 사용자가 작성한 리뷰인지"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def create(self, validated_data):
        # 현재 로그인한 사용자를 자동으로 할당
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewListSerializer(serializers.ModelSerializer):
    """리뷰 목록용 간소화된 Serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'comment', 'images', 'created_at']

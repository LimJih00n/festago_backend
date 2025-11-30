from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Event, Bookmark, Review
from .serializers import (
    EventSerializer, EventMapSerializer, BookmarkSerializer,
    ReviewSerializer, ReviewListSerializer
)


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """이벤트 API - 누구나 조회 가능"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]  # 인증 없이 조회 가능
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'location']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        """날짜가 지나지 않은 이벤트만 반환 (end_date >= 오늘)"""
        today = timezone.now().date()
        queryset = Event.objects.filter(end_date__gte=today)

        # include_past 파라미터가 있으면 모든 이벤트 반환 (관리자용)
        if self.request.query_params.get('include_past') == 'true':
            queryset = Event.objects.all()

        return queryset

    @action(detail=False, methods=['get'])
    def map(self, request):
        """지도용 엔드포인트 - 좌표가 있는 이벤트만"""
        events = self.get_queryset().filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        serializer = EventMapSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """특정 이벤트의 리뷰 목록"""
        event = self.get_object()
        reviews = event.reviews.all()
        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data)


class BookmarkViewSet(viewsets.ModelViewSet):
    """북마크 API - 인증 필수"""
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """현재 로그인한 사용자의 북마크만 조회"""
        return Bookmark.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """북마크 추가 (중복 체크)"""
        event_id = request.data.get('event_id')

        # 이미 북마크했는지 확인
        if Bookmark.objects.filter(user=request.user, event_id=event_id).exists():
            return Response(
                {'detail': '이미 북마크한 이벤트입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['delete'])
    def remove_by_event(self, request):
        """이벤트 ID로 북마크 삭제"""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {'detail': 'event_id가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bookmark = Bookmark.objects.filter(user=request.user, event_id=event_id).first()
        if not bookmark:
            return Response(
                {'detail': '북마크를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(viewsets.ModelViewSet):
    """리뷰 API"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'rating']
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        """리뷰 조회 - 모든 사용자가 볼 수 있음"""
        return Review.objects.all()

    def perform_create(self, serializer):
        """리뷰 작성 - 인증된 사용자만"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """리뷰 수정 - 본인만"""
        serializer.save()

    def perform_destroy(self, instance):
        """리뷰 삭제 - 본인만"""
        if instance.user != self.request.user:
            return Response(
                {'detail': '본인이 작성한 리뷰만 삭제할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        """내가 작성한 리뷰 목록"""
        reviews = Review.objects.filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """리뷰 생성 (중복 체크)"""
        event_id = request.data.get('event_id')

        # event_id를 정수로 변환 (프론트엔드에서 string으로 전달될 수 있음)
        try:
            event_id = int(event_id) if event_id else None
        except (ValueError, TypeError):
            return Response(
                {'detail': '유효하지 않은 이벤트 ID입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 이미 리뷰를 작성했는지 확인
        if event_id and Review.objects.filter(user=request.user, event_id=event_id).exists():
            return Response(
                {'detail': '이미 이 이벤트에 리뷰를 작성했습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

from rest_framework import serializers
from .models import Partner, Application, Message, AnalyticsData, ImageUpload, Notification, ApplicationDraft, FestivalBookmark
from events.serializers import EventSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from PIL import Image
import io

User = get_user_model()


class PartnerSignupSerializer(serializers.Serializer):
    """파트너 회원가입 Serializer"""

    # User 정보
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    # 사업자 기본 정보
    business_name = serializers.CharField(max_length=200)
    business_number = serializers.CharField(max_length=50)
    representative_name = serializers.CharField(max_length=100)
    business_type = serializers.CharField(max_length=100)
    address = serializers.CharField()
    postal_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20)
    partner_email = serializers.EmailField()
    business_certificate = serializers.URLField(required=False, allow_blank=True)

    # 브랜드 정보
    brand_name = serializers.CharField(max_length=200)
    brand_logo = serializers.URLField(required=False, allow_blank=True)
    brand_intro = serializers.CharField()
    products = serializers.CharField()

    # 선택 정보
    sns_links = serializers.JSONField(required=False)
    website = serializers.URLField(required=False, allow_blank=True)
    portfolio_images = serializers.JSONField(required=False)
    festival_images = serializers.JSONField(required=False)

    def validate_username(self, value):
        """아이디 중복 체크"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('이미 사용 중인 아이디입니다.')
        return value

    def validate_email(self, value):
        """이메일 중복 체크"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('이미 사용 중인 이메일입니다.')
        return value

    def validate_business_number(self, value):
        """사업자등록번호 중복 체크"""
        if Partner.objects.filter(business_number=value).exists():
            raise serializers.ValidationError('이미 등록된 사업자등록번호입니다.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        """User와 Partner를 함께 생성"""
        # User 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type='partner'
        )

        # Partner 생성
        partner = Partner.objects.create(
            user=user,
            business_name=validated_data['business_name'],
            business_number=validated_data['business_number'],
            representative_name=validated_data['representative_name'],
            business_type=validated_data['business_type'],
            address=validated_data['address'],
            postal_code=validated_data.get('postal_code', ''),
            phone=validated_data['phone'],
            email=validated_data['partner_email'],
            business_certificate=validated_data.get('business_certificate', ''),
            brand_name=validated_data['brand_name'],
            brand_logo=validated_data.get('brand_logo', ''),
            brand_intro=validated_data['brand_intro'],
            products=validated_data['products'],
            sns_links=validated_data.get('sns_links', {}),
            website=validated_data.get('website', ''),
            portfolio_images=validated_data.get('portfolio_images', []),
            festival_images=validated_data.get('festival_images', [])
        )

        return {
            'user': user,
            'partner': partner
        }


class PartnerSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    approval_rate = serializers.ReadOnlyField()

    class Meta:
        model = Partner
        fields = [
            "id", "user", "user_info",
            "business_name", "business_number", "representative_name", "business_type",
            "address", "postal_code", "phone", "email", "business_certificate",
            "brand_name", "brand_logo", "brand_intro", "products",
            "sns_links", "website",
            "portfolio_images", "festival_images",
            "verified", "verified_at",
            "total_applications", "total_approvals", "average_rating", "approval_rate",
            "created_at", "updated_at"
        ]
        read_only_fields = ["user", "verified", "verified_at", "total_applications", "total_approvals", "average_rating", "created_at", "updated_at"]

    def get_user_info(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }


class PartnerPublicSerializer(serializers.ModelSerializer):
    approval_rate = serializers.ReadOnlyField()
    upcoming_events = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = [
            "id",
            "brand_name", "brand_logo", "brand_intro", "products",
            "sns_links", "website",
            "portfolio_images", "festival_images",
            "average_rating", "approval_rate",
            "upcoming_events",
        ]

    def get_upcoming_events(self, obj):
        from datetime import date
        applications = obj.applications.filter(
            status="approved",
            event__start_date__gte=date.today()
        ).select_related("event")[:5]

        return [{
            "id": app.event.id,
            "name": app.event.name,
            "start_date": app.event.start_date,
            "end_date": app.event.end_date,
            "location": app.event.location,
            "booth_location": app.booth_location,
        } for app in applications]


class ApplicationSerializer(serializers.ModelSerializer):
    partner_info = serializers.SerializerMethodField()
    event_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    booth_type_display = serializers.CharField(source="get_booth_type_display", read_only=True)
    booth_size_display = serializers.CharField(source="get_booth_size_display", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id", "partner", "partner_info", "event", "event_info",
            "status", "status_display",
            "booth_type", "booth_type_display",
            "booth_size", "booth_size_display",
            "products", "price_range", "booth_location",
            "brand_intro", "brand_images",
            "has_experience", "previous_festivals", "portfolio_url",
            "special_requests",
            "organizer_message", "rejection_reason",
            "participation_fee", "payment_status", "paid_at",
            "applied_at", "reviewed_at", "updated_at"
        ]
        read_only_fields = ["partner", "organizer_message", "rejection_reason", "reviewed_at", "applied_at", "updated_at"]

    def get_partner_info(self, obj):
        return {
            "id": obj.partner.id,
            "brand_name": obj.partner.brand_name,
            "business_name": obj.partner.business_name,
        }

    def get_event_info(self, obj):
        return {
            "id": obj.event.id,
            "name": obj.event.name,
            "start_date": obj.event.start_date,
            "end_date": obj.event.end_date,
            "location": obj.event.location,
        }


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "event",
            "booth_type", "booth_size", "products", "price_range",
            "brand_intro", "brand_images",
            "has_experience", "previous_festivals", "portfolio_url",
            "special_requests",
        ]

    def create(self, validated_data):
        partner = self.context["request"].user.partner_profile
        validated_data["partner"] = partner
        partner.total_applications += 1
        partner.save()
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()
    receiver_info = serializers.SerializerMethodField()
    application_info = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id", "message_type",
            "sender", "sender_info",
            "receiver", "receiver_info",
            "application", "application_info",
            "subject", "content", "attachments",
            "read", "read_at",
            "created_at"
        ]
        read_only_fields = ["sender", "read", "read_at", "created_at"]

    def get_sender_info(self, obj):
        return {
            "id": obj.sender.id,
            "username": obj.sender.username,
        }

    def get_receiver_info(self, obj):
        if obj.receiver:
            return {
                "id": obj.receiver.id,
                "username": obj.receiver.username,
            }
        return None

    def get_application_info(self, obj):
        if obj.application:
            return {
                "id": obj.application.id,
                "event_name": obj.application.event.name,
                "partner_name": obj.application.partner.brand_name,
            }
        return None


class AnalyticsDataSerializer(serializers.ModelSerializer):
    partner_info = serializers.SerializerMethodField()
    event_info = serializers.SerializerMethodField()

    class Meta:
        model = AnalyticsData
        fields = [
            "id", "partner", "partner_info", "event", "event_info", "application",
            "visitor_count", "estimated_sales", "average_rating", "review_count",
            "hourly_visitors",
            "top_products",
            "positive_keywords", "negative_keywords", "sentiment_score",
            "previous_event_comparison",
            "generated_at", "updated_at"
        ]
        read_only_fields = ["generated_at", "updated_at"]

    def get_partner_info(self, obj):
        return {
            "id": obj.partner.id,
            "brand_name": obj.partner.brand_name,
        }

    def get_event_info(self, obj):
        return {
            "id": obj.event.id,
            "name": obj.event.name,
            "start_date": obj.event.start_date,
            "end_date": obj.event.end_date,
        }


class ImageUploadSerializer(serializers.ModelSerializer):
    """이미지 업로드 Serializer (검증 포함)"""

    file_url = serializers.SerializerMethodField()
    partner_info = serializers.SerializerMethodField()

    class Meta:
        model = ImageUpload
        fields = [
            "id", "partner", "partner_info", "image_type",
            "image", "file_url", "original_filename", "file_size",
            "width", "height", "description",
            "uploaded_at"
        ]
        read_only_fields = ["partner", "original_filename", "file_size", "width", "height", "uploaded_at"]

    def get_file_url(self, obj):
        return obj.get_file_url()

    def get_partner_info(self, obj):
        return {
            "id": obj.partner.id,
            "brand_name": obj.partner.brand_name,
        }

    def validate_image(self, value):
        """이미지 파일 검증"""
        # 파일 크기 검증 (최대 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError(f"파일 크기는 {max_size // (1024 * 1024)}MB를 초과할 수 없습니다.")

        # 파일 형식 검증 (이미지만 허용)
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(f"허용된 파일 형식: {', '.join(allowed_extensions)}")

        # 이미지 유효성 검증 (Pillow로 열 수 있는지 확인)
        try:
            img = Image.open(value)
            img.verify()
        except Exception as e:
            raise serializers.ValidationError(f"유효하지 않은 이미지 파일입니다: {str(e)}")

        return value

    def create(self, validated_data):
        """이미지 업로드 생성 및 메타데이터 저장"""
        image_file = validated_data['image']

        # 원본 파일명 저장
        validated_data['original_filename'] = image_file.name
        validated_data['file_size'] = image_file.size

        # 이미지 크기 추출
        try:
            img = Image.open(image_file)
            validated_data['width'] = img.width
            validated_data['height'] = img.height
        except Exception:
            pass

        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """알림 Serializer"""

    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    application_info = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id", "user", "notification_type", "notification_type_display",
            "title", "message",
            "link", "application", "application_info",
            "extra_data",
            "read", "read_at",
            "created_at"
        ]
        read_only_fields = ["user", "read", "read_at", "created_at"]

    def get_application_info(self, obj):
        """관련 지원서 정보"""
        if obj.application:
            return {
                "id": obj.application.id,
                "event_name": obj.application.event.name,
                "status": obj.application.status,
                "status_display": obj.application.get_status_display(),
            }
        return None


class ApplicationDraftSerializer(serializers.ModelSerializer):
    """지원서 임시저장 Serializer"""

    event_info = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationDraft
        fields = [
            "id", "partner", "event", "event_info",
            "draft_data",
            "created_at", "updated_at"
        ]
        read_only_fields = ["partner", "created_at", "updated_at"]

    def get_event_info(self, obj):
        """축제 정보"""
        return {
            "id": obj.event.id,
            "name": obj.event.name,
            "start_date": obj.event.start_date,
            "end_date": obj.event.end_date,
            "location": obj.event.location,
        }


class FestivalBookmarkSerializer(serializers.ModelSerializer):
    """축제 북마크 Serializer"""

    event_info = serializers.SerializerMethodField()

    class Meta:
        model = FestivalBookmark
        fields = [
            "id", "partner", "event", "event_info",
            "memo",
            "created_at"
        ]
        read_only_fields = ["partner", "created_at"]

    def get_event_info(self, obj):
        """축제 정보"""
        return {
            "id": obj.event.id,
            "name": obj.event.name,
            "start_date": obj.event.start_date,
            "end_date": obj.event.end_date,
            "location": obj.event.location,
            "category": obj.event.category,
        }

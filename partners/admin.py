from django.contrib import admin
from .models import Partner, Application, Message, AnalyticsData, ImageUpload, Notification, ApplicationDraft, FestivalBookmark


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'business_name', 'business_number', 'verified', 'total_applications', 'total_approvals', 'created_at']
    list_filter = ['verified', 'business_type', 'created_at']
    search_fields = ['brand_name', 'business_name', 'business_number', 'representative_name']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'business_name', 'business_number', 'representative_name', 'business_type')
        }),
        ('연락처', {
            'fields': ('phone', 'email', 'address', 'postal_code')
        }),
        ('브랜드 정보 (공개)', {
            'fields': ('brand_name', 'brand_logo', 'brand_intro', 'products', 'sns_links', 'website')
        }),
        ('포트폴리오', {
            'fields': ('portfolio_images', 'festival_images', 'business_certificate')
        }),
        ('인증 및 통계', {
            'fields': ('verified', 'verified_at', 'total_applications', 'total_approvals', 'average_rating')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['partner', 'event', 'status', 'booth_type', 'booth_size', 'payment_status', 'applied_at']
    list_filter = ['status', 'booth_type', 'booth_size', 'payment_status', 'applied_at']
    search_fields = ['partner__brand_name', 'event__name', 'products']
    readonly_fields = ['applied_at', 'reviewed_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('partner', 'event', 'status')
        }),
        ('부스 정보', {
            'fields': ('booth_type', 'booth_size', 'products', 'price_range', 'booth_location')
        }),
        ('브랜드 소개', {
            'fields': ('brand_intro', 'brand_images')
        }),
        ('참여 경험', {
            'fields': ('has_experience', 'previous_festivals', 'portfolio_url')
        }),
        ('추가 요청사항', {
            'fields': ('special_requests',)
        }),
        ('주최자 피드백', {
            'fields': ('organizer_message', 'rejection_reason')
        }),
        ('결제 정보', {
            'fields': ('participation_fee', 'payment_status', 'paid_at')
        }),
        ('타임스탬프', {
            'fields': ('applied_at', 'reviewed_at', 'updated_at')
        }),
    )

    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        for application in queryset:
            application.approve()
        self.message_user(request, f"{queryset.count()}개의 지원서를 승인했습니다.")
    approve_applications.short_description = "선택한 지원서 승인"

    def reject_applications(self, request, queryset):
        for application in queryset:
            application.reject()
        self.message_user(request, f"{queryset.count()}개의 지원서를 거절했습니다.")
    reject_applications.short_description = "선택한 지원서 거절"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'subject', 'message_type', 'read', 'created_at']
    list_filter = ['message_type', 'read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'subject', 'content']
    readonly_fields = ['created_at', 'read_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('message_type', 'sender', 'receiver', 'application')
        }),
        ('메시지 내용', {
            'fields': ('subject', 'content', 'attachments')
        }),
        ('읽음 처리', {
            'fields': ('read', 'read_at')
        }),
        ('타임스탬프', {
            'fields': ('created_at',)
        }),
    )


@admin.register(AnalyticsData)
class AnalyticsDataAdmin(admin.ModelAdmin):
    list_display = ['partner', 'event', 'visitor_count', 'estimated_sales', 'average_rating', 'review_count', 'generated_at']
    list_filter = ['generated_at', 'updated_at']
    search_fields = ['partner__brand_name', 'event__name']
    readonly_fields = ['generated_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('partner', 'event', 'application')
        }),
        ('핵심 성과 지표 (KPI)', {
            'fields': ('visitor_count', 'estimated_sales', 'average_rating', 'review_count')
        }),
        ('시간대별 데이터', {
            'fields': ('hourly_visitors',)
        }),
        ('인기 제품', {
            'fields': ('top_products',)
        }),
        ('AI 리뷰 분석', {
            'fields': ('positive_keywords', 'negative_keywords', 'sentiment_score')
        }),
        ('비교 데이터', {
            'fields': ('previous_event_comparison',)
        }),
        ('타임스탬프', {
            'fields': ('generated_at', 'updated_at')
        }),
    )


@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ['partner', 'image_type', 'original_filename', 'file_size', 'width', 'height', 'uploaded_at']
    list_filter = ['image_type', 'uploaded_at']
    search_fields = ['partner__brand_name', 'original_filename', 'description']
    readonly_fields = ['uploaded_at', 'file_size', 'width', 'height']

    fieldsets = (
        ('기본 정보', {
            'fields': ('partner', 'image_type', 'description')
        }),
        ('파일 정보', {
            'fields': ('image', 'original_filename', 'file_size', 'width', 'height')
        }),
        ('타임스탬프', {
            'fields': ('uploaded_at',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'read', 'created_at']
    list_filter = ['notification_type', 'read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'notification_type')
        }),
        ('알림 내용', {
            'fields': ('title', 'message')
        }),
        ('연결 정보', {
            'fields': ('link', 'application', 'extra_data')
        }),
        ('읽음 처리', {
            'fields': ('read', 'read_at')
        }),
        ('타임스탬프', {
            'fields': ('created_at',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f"{queryset.count()}개의 알림을 읽음 처리했습니다.")
    mark_as_read.short_description = "선택한 알림 읽음 처리"

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False, read_at=None)
        self.message_user(request, f"{queryset.count()}개의 알림을 읽지않음 처리했습니다.")
    mark_as_unread.short_description = "선택한 알림 읽지않음 처리"


@admin.register(ApplicationDraft)
class ApplicationDraftAdmin(admin.ModelAdmin):
    list_display = ['partner', 'event', 'updated_at', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['partner__brand_name', 'event__name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('partner', 'event')
        }),
        ('임시저장 데이터', {
            'fields': ('draft_data',)
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(FestivalBookmark)
class FestivalBookmarkAdmin(admin.ModelAdmin):
    list_display = ['partner', 'event', 'created_at']
    list_filter = ['created_at']
    search_fields = ['partner__brand_name', 'event__name', 'memo']
    readonly_fields = ['created_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('partner', 'event')
        }),
        ('메모', {
            'fields': ('memo',)
        }),
        ('타임스탬프', {
            'fields': ('created_at',)
        }),
    )

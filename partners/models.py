from django.db import models
from django.conf import settings
from django.utils import timezone


class Partner(models.Model):
    """사업자 프로필 - User 확장 모델"""

    # User 연결 (OneToOne)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partner_profile'
    )

    # === 사업자 기본 정보 (비공개) ===
    business_name = models.CharField(max_length=200, verbose_name='상호명')
    business_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='사업자등록번호'
    )
    representative_name = models.CharField(max_length=100, verbose_name='대표자명')
    business_type = models.CharField(max_length=100, verbose_name='업종')

    # 사업장 주소
    address = models.TextField(verbose_name='사업장 주소')
    postal_code = models.CharField(max_length=10, blank=True)

    # 연락처
    phone = models.CharField(max_length=20, verbose_name='대표 연락처')
    email = models.EmailField(verbose_name='이메일')

    # 사업자등록증 (인증용)
    business_certificate = models.URLField(
        blank=True,
        verbose_name='사업자등록증 이미지'
    )

    # === 브랜드 정보 (공개용) ===
    brand_name = models.CharField(
        max_length=200,
        verbose_name='브랜드명'
    )
    brand_logo = models.URLField(
        blank=True,
        verbose_name='브랜드 로고'
    )
    brand_intro = models.TextField(
        verbose_name='브랜드 소개',
        help_text='일반 유저에게 공개되는 소개글'
    )
    products = models.TextField(
        verbose_name='대표 제품/메뉴',
        help_text='판매하는 제품 목록'
    )

    # SNS 링크
    sns_links = models.JSONField(
        default=dict,
        blank=True,
        help_text='{"instagram": "@username", "facebook": "...", "youtube": "..."}'
    )
    website = models.URLField(blank=True, verbose_name='공식 웹사이트')

    # 포트폴리오
    portfolio_images = models.JSONField(
        default=list,
        blank=True,
        help_text='제품/메뉴 사진 URL 리스트'
    )
    festival_images = models.JSONField(
        default=list,
        blank=True,
        help_text='이전 축제 참여 사진 URL 리스트'
    )

    # === 인증 및 검증 ===
    verified = models.BooleanField(
        default=False,
        verbose_name='사업자 인증 완료'
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='인증 완료 일시'
    )

    # 통계
    total_applications = models.IntegerField(
        default=0,
        verbose_name='총 지원 횟수'
    )
    total_approvals = models.IntegerField(
        default=0,
        verbose_name='총 승인 횟수'
    )
    average_rating = models.FloatField(
        default=0,
        verbose_name='평균 평점'
    )

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '사업자'
        verbose_name_plural = '사업자 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand_name} ({self.business_name})"

    @property
    def approval_rate(self):
        """승인률 계산"""
        if self.total_applications == 0:
            return 0
        return round((self.total_approvals / self.total_applications) * 100, 1)


class Application(models.Model):
    """축제 참여 지원서"""

    STATUS_CHOICES = [
        ('pending', '검토중'),
        ('approved', '승인됨'),
        ('rejected', '거절됨'),
        ('cancelled', '취소됨'),
        ('completed', '완료'),
    ]

    BOOTH_TYPE_CHOICES = [
        ('food', '음식 부스'),
        ('goods', '굿즈 판매'),
        ('experience', '체험 부스'),
        ('promotion', '홍보 부스'),
    ]

    BOOTH_SIZE_CHOICES = [
        ('3x3', '3x3m (기본형)'),
        ('6x3', '6x3m (대형)'),
        ('custom', '맞춤형'),
    ]

    # === 기본 정보 ===
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='applications'
    )

    # === 지원 상태 ===
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # === 부스 정보 ===
    booth_type = models.CharField(
        max_length=20,
        choices=BOOTH_TYPE_CHOICES,
        verbose_name='부스 종류'
    )
    booth_size = models.CharField(
        max_length=10,
        choices=BOOTH_SIZE_CHOICES,
        default='3x3',
        verbose_name='부스 크기'
    )
    products = models.TextField(
        verbose_name='판매/전시 품목',
        help_text='예: 김밥, 떡볶이, 음료'
    )
    price_range = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='가격대',
        help_text='예: 3,000원 ~ 8,000원'
    )

    # === 브랜드 소개 (지원서용) ===
    brand_intro = models.TextField(
        verbose_name='브랜드 소개',
        help_text='이 축제에 지원하는 이유 및 브랜드 소개'
    )
    brand_images = models.JSONField(
        default=list,
        blank=True,
        help_text='지원서에 첨부할 브랜드 이미지 URL 리스트'
    )

    # === 참여 경험 ===
    has_experience = models.BooleanField(
        default=False,
        verbose_name='이전 축제 참여 경험 있음'
    )
    previous_festivals = models.TextField(
        blank=True,
        verbose_name='이전 참여 축제 목록'
    )
    portfolio_url = models.URLField(
        blank=True,
        verbose_name='포트폴리오 URL'
    )

    # === 추가 요청사항 ===
    special_requests = models.TextField(
        blank=True,
        verbose_name='추가 요청사항',
        help_text='예: 냉장고 필요, 전기 콘센트 2개 필요'
    )

    # === 주최자 피드백 ===
    organizer_message = models.TextField(
        blank=True,
        verbose_name='주최자 메시지'
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='거절 사유'
    )

    # === 결제 정보 ===
    participation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='참가비'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', '미결제'),
            ('paid', '결제완료'),
            ('refunded', '환불완료'),
        ],
        default='unpaid'
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    # === 부스 배정 정보 ===
    booth_location = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='부스 위치',
        help_text='예: A-12'
    )

    # === 타임스탬프 ===
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='지원일')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='검토일')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '축제 지원서'
        verbose_name_plural = '축제 지원서 목록'
        ordering = ['-applied_at']
        unique_together = ['partner', 'event']  # 한 사업자가 같은 축제에 중복 지원 불가

    def __str__(self):
        return f"{self.partner.brand_name} → {self.event.name} ({self.get_status_display()})"

    def approve(self, organizer_message=''):
        """지원서 승인"""
        self.status = 'approved'
        self.organizer_message = organizer_message
        self.reviewed_at = timezone.now()
        self.save()

        # Partner 통계 업데이트
        self.partner.total_approvals += 1
        self.partner.save()

    def reject(self, rejection_reason=''):
        """지원서 거절"""
        self.status = 'rejected'
        self.rejection_reason = rejection_reason
        self.reviewed_at = timezone.now()
        self.save()


class Message(models.Model):
    """주최자-사업자 간 메시지"""

    MESSAGE_TYPE_CHOICES = [
        ('direct', '1:1 메시지'),
        ('announcement', '전체 공지'),
    ]

    # === 기본 정보 ===
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='direct'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True,
        blank=True,
        help_text='전체 공지인 경우 null'
    )

    # 관련 지원서 (선택)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True
    )

    # === 메시지 내용 ===
    subject = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')

    # 첨부파일
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text='파일 URL 리스트'
    )

    # === 읽음 처리 ===
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # === 타임스탬프 ===
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '메시지'
        verbose_name_plural = '메시지 목록'
        ordering = ['-created_at']

    def __str__(self):
        if self.message_type == 'announcement':
            return f"[공지] {self.subject}"
        return f"{self.sender.username} → {self.receiver.username}: {self.subject}"

    def mark_as_read(self):
        """읽음 처리"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()


class AnalyticsData(models.Model):
    """사업자별 축제 성과 데이터 (중간보고서 핵심!)"""

    # === 기본 정보 ===
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='partner_analytics'
    )
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='analytics'
    )

    # === 핵심 성과 지표 (KPI) ===
    visitor_count = models.IntegerField(
        default=0,
        verbose_name='방문객 수',
        help_text='주최측 제공 데이터'
    )
    estimated_sales = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='예상 판매액'
    )
    average_rating = models.FloatField(
        default=0,
        verbose_name='평균 평점'
    )
    review_count = models.IntegerField(
        default=0,
        verbose_name='리뷰 개수'
    )

    # === 시간대별 데이터 ===
    hourly_visitors = models.JSONField(
        default=dict,
        blank=True,
        help_text='{"10": 120, "11": 250, ...}'
    )

    # === 인기 제품 ===
    top_products = models.JSONField(
        default=list,
        blank=True,
        help_text='[{"name": "참치김밥", "clicks": 485, "avg_time": 15}, ...]'
    )

    # === AI 리뷰 분석 ===
    positive_keywords = models.JSONField(
        default=list,
        blank=True,
        help_text='긍정 키워드 및 빈도'
    )
    negative_keywords = models.JSONField(
        default=list,
        blank=True,
        help_text='부정 키워드 및 빈도'
    )
    sentiment_score = models.FloatField(
        default=0,
        verbose_name='감성 점수',
        help_text='0-100 (높을수록 긍정적)'
    )

    # === 비교 데이터 ===
    previous_event_comparison = models.JSONField(
        default=dict,
        blank=True,
        help_text='이전 축제와 비교 데이터'
    )

    # === 타임스탬프 ===
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '성과 데이터'
        verbose_name_plural = '성과 데이터 목록'
        unique_together = ['partner', 'event']

    def __str__(self):
        return f"{self.partner.brand_name} - {self.event.name} 성과"


class ImageUpload(models.Model):
    """파일 업로드 관리 모델"""

    IMAGE_TYPE_CHOICES = [
        ('certificate', '사업자등록증'),
        ('logo', '브랜드 로고'),
        ('portfolio', '포트폴리오'),
        ('product', '제품 사진'),
        ('festival', '축제 참여 사진'),
        ('other', '기타'),
    ]

    # === 기본 정보 ===
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        verbose_name='이미지 종류'
    )

    # === 파일 정보 ===
    image = models.ImageField(
        upload_to='partners/%Y/%m/%d/',
        verbose_name='이미지 파일'
    )
    original_filename = models.CharField(
        max_length=255,
        verbose_name='원본 파일명'
    )
    file_size = models.IntegerField(
        verbose_name='파일 크기 (bytes)'
    )

    # === 이미지 메타데이터 ===
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    # === 설명 ===
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='설명'
    )

    # === 타임스탬프 ===
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '이미지 업로드'
        verbose_name_plural = '이미지 업로드 목록'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.partner.brand_name} - {self.get_image_type_display()} ({self.uploaded_at.strftime('%Y-%m-%d')})"

    def get_file_url(self):
        """이미지 URL 반환"""
        if self.image:
            return self.image.url
        return None


class Notification(models.Model):
    """알림 모델"""

    TYPE_CHOICES = [
        ('application_submitted', '지원서 제출'),
        ('application_approved', '지원서 승인'),
        ('application_rejected', '지원서 거절'),
        ('message_received', '새 메시지'),
        ('event_reminder', '이벤트 알림'),
        ('payment_required', '결제 필요'),
        ('booth_assigned', '부스 배정'),
        ('analytics_ready', '성과 데이터 준비'),
        ('system', '시스템 알림'),
    ]

    # === 기본 정보 ===
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='수신자'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name='알림 유형'
    )

    # === 알림 내용 ===
    title = models.CharField(max_length=200, verbose_name='제목')
    message = models.TextField(verbose_name='메시지')

    # === 연결 정보 ===
    link = models.URLField(
        blank=True,
        verbose_name='연결 링크',
        help_text='클릭 시 이동할 URL'
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name='관련 지원서'
    )

    # === 추가 데이터 ===
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='추가 메타데이터'
    )

    # === 읽음 처리 ===
    read = models.BooleanField(default=False, verbose_name='읽음')
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='읽은 시각'
    )

    # === 타임스탬프 ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시각')

    class Meta:
        verbose_name = '알림'
        verbose_name_plural = '알림 목록'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.get_notification_type_display()})"

    def mark_as_read(self):
        """읽음 처리"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save(update_fields=['read', 'read_at'])


class ApplicationDraft(models.Model):
    """지원서 임시저장"""

    # === 기본 정보 ===
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='drafts',
        verbose_name='사업자'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='application_drafts',
        verbose_name='축제'
    )

    # === 임시저장 데이터 (JSON) ===
    draft_data = models.JSONField(
        default=dict,
        verbose_name='임시저장 데이터',
        help_text='작성 중인 지원서 데이터'
    )

    # === 타임스탬프 ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시각')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시각')

    class Meta:
        verbose_name = '임시저장 지원서'
        verbose_name_plural = '임시저장 지원서 목록'
        unique_together = ['partner', 'event']  # 축제당 하나의 임시저장만
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.partner.brand_name} - {self.event.name} (임시저장)"


class FestivalBookmark(models.Model):
    """축제 북마크 (관심 축제)"""

    # === 기본 정보 ===
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='사업자'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='bookmarked_by',
        verbose_name='축제'
    )

    # === 메모 ===
    memo = models.TextField(
        blank=True,
        verbose_name='메모',
        help_text='북마크 메모 (선택)'
    )

    # === 타임스탬프 ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='북마크 일시')

    class Meta:
        verbose_name = '축제 북마크'
        verbose_name_plural = '축제 북마크 목록'
        unique_together = ['partner', 'event']  # 중복 북마크 방지
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.partner.brand_name} ❤️ {self.event.name}"

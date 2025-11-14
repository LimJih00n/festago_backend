"""
샘플 데이터 생성 Management Command
Usage: python manage.py generate_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
import random
from decimal import Decimal

from partners.models import Partner, Application, Message, AnalyticsData
from events.models import Event

User = get_user_model()


class Command(BaseCommand):
    help = '사업자 샘플 데이터 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터 삭제 후 생성',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('기존 데이터 삭제 중...')
            Partner.objects.all().delete()
            User.objects.filter(user_type='partner').delete()
            self.stdout.write(self.style.SUCCESS('기존 데이터 삭제 완료'))

        self.stdout.write('샘플 데이터 생성 시작...')

        # 1. 사업자 유저 및 프로필 생성
        partners = self.create_partners()
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(partners)}개의 사업자 생성 완료'))

        # 2. 이벤트 확인 (최소 5개 필요)
        events = list(Event.objects.all()[:10])
        if len(events) < 5:
            self.stdout.write(self.style.WARNING(
                f'[WARN] 이벤트가 {len(events)}개만 있습니다. 최소 5개 필요'
            ))
            if len(events) == 0:
                self.stdout.write(self.style.ERROR('이벤트가 없어 지원서를 생성할 수 없습니다.'))
                return

        # 3. 지원서 생성
        applications = self.create_applications(partners, events)
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(applications)}개의 지원서 생성 완료'))

        # 4. 메시지 생성
        messages = self.create_messages(applications)
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(messages)}개의 메시지 생성 완료'))

        # 5. 성과 데이터 생성
        analytics = self.create_analytics(applications)
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(analytics)}개의 성과 데이터 생성 완료'))

        self.stdout.write(self.style.SUCCESS('\n=== 샘플 데이터 생성 완료! ==='))
        self.stdout.write(f'사업자: {len(partners)}개')
        self.stdout.write(f'지원서: {len(applications)}개')
        self.stdout.write(f'메시지: {len(messages)}개')
        self.stdout.write(f'성과 데이터: {len(analytics)}개')

    def create_partners(self):
        """사업자 10개 생성"""
        partners_data = [
            {
                'username': 'partner_kim',
                'email': 'kim@foodtruck.com',
                'business_name': '김씨네푸드트럭',
                'brand_name': '김씨네 떡볶이',
                'business_type': '음식점업',
                'products': '떡볶이, 순대, 튀김',
                'brand_intro': '25년 전통의 맛있는 떡볶이를 축제에서 만나보세요!',
            },
            {
                'username': 'partner_lee',
                'email': 'lee@coffeeshop.com',
                'business_name': '이씨커피',
                'brand_name': 'Lee\'s Coffee',
                'business_type': '카페',
                'products': '커피, 음료, 디저트',
                'brand_intro': '신선한 원두로 내린 스페셜티 커피',
            },
            {
                'username': 'partner_park',
                'email': 'park@goods.com',
                'business_name': '박씨굿즈',
                'brand_name': 'Park Goods',
                'business_type': '소매업',
                'products': '핸드메이드 굿즈, 액세서리',
                'brand_intro': '수제 악세서리와 독특한 굿즈를 판매합니다',
            },
            {
                'username': 'partner_choi',
                'email': 'choi@chicken.com',
                'business_name': '최고치킨',
                'brand_name': '최고의치킨',
                'business_type': '음식점업',
                'products': '치킨, 감자튀김',
                'brand_intro': '바삭바삭한 치킨의 정석',
            },
            {
                'username': 'partner_jung',
                'email': 'jung@icecream.com',
                'business_name': '정씨아이스크림',
                'brand_name': 'Jung Ice Cream',
                'business_type': '음식점업',
                'products': '수제 아이스크림, 젤라또',
                'brand_intro': '천연 재료로 만든 프리미엄 아이스크림',
            },
            {
                'username': 'partner_kang',
                'email': 'kang@craft.com',
                'business_name': '강씨공방',
                'brand_name': '강씨 핸드크래프트',
                'business_type': '제조업',
                'products': '가죽공예, 수제가방',
                'brand_intro': '정성스럽게 만든 핸드메이드 가죽제품',
            },
            {
                'username': 'partner_yoon',
                'email': 'yoon@burger.com',
                'business_name': '윤씨버거',
                'brand_name': 'Yoon Burger',
                'business_type': '음식점업',
                'products': '수제버거, 감자튀김, 음료',
                'brand_intro': '신선한 재료로 만드는 프리미엄 버거',
            },
            {
                'username': 'partner_lim',
                'email': 'lim@clothing.com',
                'business_name': '림씨의류',
                'brand_name': 'Lim Fashion',
                'business_type': '소매업',
                'products': '의류, 액세서리',
                'brand_intro': '트렌디한 스트릿 패션',
            },
            {
                'username': 'partner_han',
                'email': 'han@dessert.com',
                'business_name': '한씨디저트',
                'brand_name': '한씨 마카롱',
                'business_type': '제과점',
                'products': '마카롱, 케이크, 쿠키',
                'brand_intro': '달콤한 수제 디저트 전문점',
            },
            {
                'username': 'partner_oh',
                'email': 'oh@photo.com',
                'business_name': '오씨포토',
                'brand_name': 'Oh Photo Booth',
                'business_type': '서비스업',
                'products': '포토부스, 인화 서비스',
                'brand_intro': '추억을 남기는 즉석 사진 서비스',
            },
        ]

        partners = []
        for i, data in enumerate(partners_data):
            # User 생성
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='testpass123',
                user_type='partner'
            )

            # Partner 프로필 생성
            partner = Partner.objects.create(
                user=user,
                business_name=data['business_name'],
                business_number=f'123-45-{67890 + i}',
                representative_name=data['username'].split('_')[1].capitalize(),
                business_type=data['business_type'],
                address=f'서울시 강남구 테헤란로 {random.randint(100, 500)}',
                postal_code=f'0{random.randint(6000, 6999)}',
                phone=f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                email=data['email'],
                brand_name=data['brand_name'],
                brand_intro=data['brand_intro'],
                products=data['products'],
                verified=random.choice([True, True, True, False]),  # 75% 인증됨
                sns_links={
                    'instagram': f'@{data["username"]}',
                    'facebook': f'{data["username"]}_official'
                }
            )
            partners.append(partner)

        return partners

    def create_applications(self, partners, events):
        """지원서 30개 생성 (다양한 상태)"""
        applications = []
        statuses = ['pending', 'approved', 'rejected', 'completed']
        booth_types = ['food', 'goods', 'experience', 'promotion']

        for partner in partners:
            # 각 사업자당 3개의 지원서 생성
            num_apps = random.randint(2, 4)
            selected_events = random.sample(events, min(num_apps, len(events)))

            for event in selected_events:
                status_choice = random.choice(statuses)

                # 과거 이벤트는 'completed' 상태로
                if event.end_date < date.today():
                    status_choice = 'completed'

                app = Application.objects.create(
                    partner=partner,
                    event=event,
                    status=status_choice,
                    booth_type=random.choice(booth_types),
                    booth_size=random.choice(['3x3', '6x3']),
                    products=partner.products,
                    price_range=f'{random.randint(3, 10) * 1000}원 ~ {random.randint(10, 20) * 1000}원',
                    brand_intro=f'{event.name}에 참여하여 {partner.brand_name}의 제품을 선보이고 싶습니다.',
                    has_experience=random.choice([True, False]),
                    previous_festivals='서울 푸드트럭 축제, 한강 음악 페스티벌' if random.choice([True, False]) else '',
                    participation_fee=Decimal(random.randint(50, 200)) * Decimal('1000'),
                    payment_status='paid' if status_choice in ['approved', 'completed'] else 'unpaid',
                )

                # 승인/거절된 경우 피드백 추가
                if status_choice == 'approved':
                    app.organizer_message = '축하합니다! 지원이 승인되었습니다. 부스 위치는 추후 안내드리겠습니다.'
                    app.reviewed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                    app.booth_location = f'{random.choice(["A", "B", "C"])}-{random.randint(1, 30)}'
                    app.save()
                elif status_choice == 'rejected':
                    app.rejection_reason = random.choice([
                        '이번 축제는 음식 부스 신청이 마감되었습니다.',
                        '브랜드 컨셉이 이번 축제 테마와 맞지 않습니다.',
                        '동일 카테고리 부스가 이미 많이 선정되었습니다.'
                    ])
                    app.reviewed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                    app.save()
                elif status_choice == 'completed':
                    app.organizer_message = '성공적인 축제 참여 감사합니다!'
                    app.reviewed_at = event.end_date - timedelta(days=7)
                    app.booth_location = f'{random.choice(["A", "B", "C"])}-{random.randint(1, 30)}'
                    app.save()

                # Partner 통계 업데이트
                partner.total_applications += 1
                if status_choice in ['approved', 'completed']:
                    partner.total_approvals += 1
                partner.save()

                applications.append(app)

        return applications

    def create_messages(self, applications):
        """메시지 20개 생성"""
        messages = []

        # 관리자 유저 생성 (주최자 역할)
        organizer, _ = User.objects.get_or_create(
            username='organizer_main',
            defaults={
                'email': 'organizer@festago.com',
                'user_type': 'organizer'
            }
        )

        # 승인/거절된 지원서에 메시지 추가
        reviewed_apps = [app for app in applications if app.status in ['approved', 'rejected', 'completed']]
        selected_apps = random.sample(reviewed_apps, min(20, len(reviewed_apps)))

        for app in selected_apps:
            if app.status == 'approved':
                msg = Message.objects.create(
                    message_type='direct',
                    sender=organizer,
                    receiver=app.partner.user,
                    application=app,
                    subject=f'{app.event.name} 지원 승인 안내',
                    content=f'안녕하세요, {app.partner.brand_name} 님!\n\n{app.event.name} 지원이 승인되었습니다.\n부스 위치: {app.booth_location}\n\n준비 사항은 추후 안내드리겠습니다.\n감사합니다!',
                    read=random.choice([True, False])
                )
            elif app.status == 'rejected':
                msg = Message.objects.create(
                    message_type='direct',
                    sender=organizer,
                    receiver=app.partner.user,
                    application=app,
                    subject=f'{app.event.name} 지원 결과 안내',
                    content=f'안녕하세요, {app.partner.brand_name} 님!\n\n아쉽게도 이번에는 선정되지 못하셨습니다.\n사유: {app.rejection_reason}\n\n다음 기회에 다시 지원 부탁드립니다.\n감사합니다!',
                    read=random.choice([True, False])
                )
            else:  # completed
                msg = Message.objects.create(
                    message_type='direct',
                    sender=organizer,
                    receiver=app.partner.user,
                    application=app,
                    subject=f'{app.event.name} 참여 감사합니다',
                    content=f'안녕하세요, {app.partner.brand_name} 님!\n\n{app.event.name} 성공적으로 마무리되었습니다.\n참여해 주셔서 감사합니다!\n\n성과 데이터를 확인해 보세요.',
                    read=True
                )

            if msg.read:
                msg.read_at = timezone.now() - timedelta(hours=random.randint(1, 72))
                msg.save()

            messages.append(msg)

        return messages

    def create_analytics(self, applications):
        """성과 데이터 15개 생성"""
        analytics_list = []

        # 완료된 지원서에 대해서만 성과 데이터 생성
        completed_apps = [app for app in applications if app.status == 'completed']
        selected_apps = random.sample(completed_apps, min(15, len(completed_apps)))

        for app in selected_apps:
            # 시간대별 방문객 데이터
            hourly_data = {}
            for hour in range(10, 22):  # 10시~21시
                hourly_data[str(hour)] = random.randint(50, 300)

            # 인기 제품 데이터
            products_list = app.products.split(', ')
            top_products = []
            for i, product in enumerate(products_list[:3]):
                top_products.append({
                    'rank': i + 1,
                    'name': product,
                    'sales': random.randint(50, 200),
                    'revenue': random.randint(100000, 500000)
                })

            # AI 리뷰 분석 (키워드)
            positive_keywords = [
                {'word': '맛있어요', 'count': random.randint(20, 80)},
                {'word': '친절해요', 'count': random.randint(15, 60)},
                {'word': '신선해요', 'count': random.randint(10, 50)},
            ]
            negative_keywords = [
                {'word': '줄이 길어요', 'count': random.randint(5, 20)},
                {'word': '가격이 비싸요', 'count': random.randint(3, 15)},
            ]

            analytics = AnalyticsData.objects.create(
                partner=app.partner,
                event=app.event,
                application=app,
                visitor_count=sum(hourly_data.values()),
                estimated_sales=Decimal(random.randint(500, 3000)) * Decimal('1000'),
                average_rating=round(random.uniform(3.5, 5.0), 1),
                review_count=random.randint(20, 150),
                hourly_visitors=hourly_data,
                top_products=top_products,
                positive_keywords=positive_keywords,
                negative_keywords=negative_keywords,
                sentiment_score=round(random.uniform(60, 95), 1),
            )
            analytics_list.append(analytics)

        return analytics_list

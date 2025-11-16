from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = '테스트용 계정 2개를 생성합니다'

    def handle(self, *args, **options):
        # 테스트 계정 정보
        test_users = [
            {
                'username': 'testuser',
                'email': 'user@naver.com',
                'password': 'test1234',
                'user_type': 'consumer'
            },
            {
                'username': 'testadmin',
                'email': 'admin@naver.com',
                'password': 'test1234',
                'user_type': 'partner'
            }
        ]

        for user_data in test_users:
            email = user_data['email']

            # 이미 존재하는 계정인지 확인
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'계정 {email}이 이미 존재합니다. 건너뜁니다.')
                )
                continue

            # 계정 생성
            user = User.objects.create_user(
                username=user_data['username'],
                email=email,
                password=user_data['password'],
                user_type=user_data['user_type']
            )

            self.stdout.write(
                self.style.SUCCESS(f'계정 생성 완료: {email} (타입: {user_data["user_type"]})')
            )

        self.stdout.write(self.style.SUCCESS('\n테스트 계정 생성이 완료되었습니다!'))
        self.stdout.write('로그인 정보:')
        self.stdout.write('  - 일반 사용자: user@naver.com / test1234')
        self.stdout.write('  - 파트너: admin@naver.com / test1234')

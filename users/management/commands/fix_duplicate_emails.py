from django.core.management.base import BaseCommand
from django.db.models import Count
from users.models import User


class Command(BaseCommand):
    help = '중복된 이메일을 가진 유저를 찾아서 수정합니다'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("중복 이메일 유저 검사 및 수정")
        self.stdout.write("=" * 80)

        # 중복된 이메일 찾기
        duplicates = (
            User.objects.values('email')
            .annotate(email_count=Count('email'))
            .filter(email_count__gt=1)
            .exclude(email='')  # 빈 이메일은 제외
        )

        if not duplicates:
            self.stdout.write(self.style.SUCCESS("\n✓ 중복된 이메일이 없습니다!"))
            return

        self.stdout.write(self.style.WARNING(f"\n중복된 이메일 발견: {duplicates.count()}개\n"))

        total_deleted = 0

        for dup in duplicates:
            email = dup['email']
            count = dup['email_count']
            users = User.objects.filter(email=email).order_by('date_joined')

            self.stdout.write(f"\n이메일: {email} ({count}개 계정)")
            for i, user in enumerate(users, 1):
                last_login_str = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '없음'
                self.stdout.write(
                    f"  {i}. ID: {user.id}, Username: {user.username}, "
                    f"가입일: {user.date_joined.strftime('%Y-%m-%d %H:%M')}, "
                    f"마지막 로그인: {last_login_str}"
                )

            # 가장 오래된 계정만 남기고 나머지 삭제
            keep_user = users.first()  # 가장 먼저 가입한 계정
            delete_users = users.exclude(id=keep_user.id)

            self.stdout.write(
                self.style.SUCCESS(f"  → 보존: {keep_user.username} (ID: {keep_user.id})")
            )
            self.stdout.write(
                self.style.WARNING(
                    f"  → 삭제: {', '.join([f'{u.username} (ID: {u.id})' for u in delete_users])}"
                )
            )

            # 삭제 실행
            deleted_count = delete_users.delete()[0]
            total_deleted += deleted_count
            self.stdout.write(self.style.SUCCESS(f"  ✓ {deleted_count}개 계정 삭제 완료"))

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.SUCCESS(f"완료! 총 {total_deleted}개 계정 삭제됨")
        )
        self.stdout.write("=" * 80)

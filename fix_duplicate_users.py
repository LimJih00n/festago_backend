"""
중복된 이메일을 가진 유저를 찾아서 수정하는 스크립트
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db.models import Count
from users.models import User

def find_duplicate_emails():
    """중복된 이메일을 가진 유저 찾기"""
    duplicates = (
        User.objects.values('email')
        .annotate(email_count=Count('email'))
        .filter(email_count__gt=1)
        .exclude(email='')  # 빈 이메일은 제외
    )

    print(f"중복된 이메일 발견: {duplicates.count()}개")
    print("-" * 80)

    for dup in duplicates:
        email = dup['email']
        count = dup['email_count']
        users = User.objects.filter(email=email).order_by('date_joined')

        print(f"\n이메일: {email} ({count}개 계정)")
        for i, user in enumerate(users, 1):
            print(f"  {i}. ID: {user.id}, Username: {user.username}, "
                  f"가입일: {user.date_joined}, 마지막 로그인: {user.last_login}")

        # 가장 오래된 계정만 남기고 나머지 삭제
        if count > 1:
            keep_user = users.first()  # 가장 먼저 가입한 계정
            delete_users = users.exclude(id=keep_user.id)

            print(f"\n  → 보존: {keep_user.username} (ID: {keep_user.id})")
            print(f"  → 삭제 예정: {', '.join([f'{u.username} (ID: {u.id})' for u in delete_users])}")

            # 삭제 확인
            confirm = input(f"\n  이 계정들을 삭제하시겠습니까? (y/N): ")
            if confirm.lower() == 'y':
                deleted_count = delete_users.delete()[0]
                print(f"  ✓ {deleted_count}개 계정 삭제 완료")
            else:
                print("  ✗ 삭제 취소")

if __name__ == '__main__':
    print("=" * 80)
    print("중복 유저 검사 및 수정 스크립트")
    print("=" * 80)

    find_duplicate_emails()

    print("\n" + "=" * 80)
    print("완료!")
    print("=" * 80)

"""
파트너 샘플 데이터가 없는 경우에만 생성하는 Management Command
Render 빌드 시 자동으로 실행됨
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from partners.models import Partner, AnalyticsData


class Command(BaseCommand):
    help = '파트너 샘플 데이터가 없는 경우에만 생성합니다'

    def handle(self, *args, **options):
        partner_count = Partner.objects.count()
        analytics_count = AnalyticsData.objects.count()

        if partner_count == 0:
            self.stdout.write(
                self.style.WARNING('파트너 데이터가 없습니다. 샘플 데이터를 생성합니다...')
            )
            call_command('generate_sample_data')
            self.stdout.write(
                self.style.SUCCESS('샘플 데이터 생성 완료!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'이미 {partner_count}개의 파트너, {analytics_count}개의 성과 데이터가 있습니다. '
                    f'샘플 데이터 생성을 건너뜁니다.'
                )
            )

"""
Django Signals for Partners App
지원서 상태 변경 시 자동 알림 생성
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Application, Message, Notification, AnalyticsData


@receiver(pre_save, sender=Application)
def track_application_status_change(sender, instance, **kwargs):
    """지원서 상태 변경 추적"""
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Application)
def application_status_changed(sender, instance, created, **kwargs):
    """
    지원서 상태 변경 시 알림 생성
    - 지원서 제출 (created=True)
    - 승인 (status changed to 'approved')
    - 거절 (status changed to 'rejected')
    - 완료 (status changed to 'completed')
    """
    user = instance.partner.user
    event_name = instance.event.name

    # 새로 생성된 지원서 (제출)
    if created:
        Notification.objects.create(
            user=user,
            notification_type='application_submitted',
            title='지원서 제출 완료',
            message=f'{event_name}에 지원서를 제출했습니다. 검토 결과를 기다려 주세요.',
            link=f'/partner/applications',
            application=instance,
            extra_data={
                'event_id': instance.event.id,
                'event_name': event_name,
            }
        )
        return

    # 상태 변경 확인
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    if old_status == new_status:
        return  # 상태 변경 없음

    # 승인됨
    if new_status == 'approved':
        Notification.objects.create(
            user=user,
            notification_type='application_approved',
            title=f'{event_name} 지원 승인!',
            message=f'축하합니다! {event_name} 지원이 승인되었습니다.\n부스 위치: {instance.booth_location or "추후 안내"}',
            link=f'/partner/applications',
            application=instance,
            extra_data={
                'event_id': instance.event.id,
                'event_name': event_name,
                'booth_location': instance.booth_location,
                'organizer_message': instance.organizer_message,
            }
        )

        # 결제 필요 알림 (미결제 상태인 경우)
        if instance.payment_status == 'unpaid' and instance.participation_fee > 0:
            Notification.objects.create(
                user=user,
                notification_type='payment_required',
                title='참가비 결제 필요',
                message=f'{event_name} 참가비({instance.participation_fee}원)를 결제해 주세요.',
                link=f'/partner/applications',
                application=instance,
                extra_data={
                    'event_id': instance.event.id,
                    'event_name': event_name,
                    'amount': str(instance.participation_fee),
                }
            )

    # 거절됨
    elif new_status == 'rejected':
        Notification.objects.create(
            user=user,
            notification_type='application_rejected',
            title=f'{event_name} 지원 결과 안내',
            message=f'아쉽게도 {event_name} 지원이 선정되지 못했습니다.\n사유: {instance.rejection_reason or "자세한 내용은 주최측 메시지를 확인해 주세요."}',
            link=f'/partner/applications',
            application=instance,
            extra_data={
                'event_id': instance.event.id,
                'event_name': event_name,
                'rejection_reason': instance.rejection_reason,
            }
        )

    # 완료됨
    elif new_status == 'completed':
        Notification.objects.create(
            user=user,
            notification_type='analytics_ready',
            title=f'{event_name} 참여 완료',
            message=f'{event_name} 축제가 성공적으로 마무리되었습니다. 성과 데이터를 확인해 보세요!',
            link=f'/partner/analytics',
            application=instance,
            extra_data={
                'event_id': instance.event.id,
                'event_name': event_name,
            }
        )


@receiver(post_save, sender=Message)
def message_received(sender, instance, created, **kwargs):
    """
    새 메시지 수신 시 알림 생성
    """
    if created and instance.receiver:
        # 받는 사람에게만 알림 생성
        Notification.objects.create(
            user=instance.receiver,
            notification_type='message_received',
            title='새 메시지',
            message=f'{instance.sender.username}님으로부터 새 메시지가 도착했습니다.\n제목: {instance.subject}',
            link=f'/partner/messages',
            application=instance.application,
            extra_data={
                'message_id': instance.id,
                'sender': instance.sender.username,
                'subject': instance.subject,
            }
        )


@receiver(post_save, sender=AnalyticsData)
def analytics_ready(sender, instance, created, **kwargs):
    """
    성과 데이터 생성 시 알림
    """
    if created:
        user = instance.partner.user
        event_name = instance.event.name

        Notification.objects.create(
            user=user,
            notification_type='analytics_ready',
            title='성과 데이터 준비 완료',
            message=f'{event_name}의 성과 데이터가 생성되었습니다. 지금 확인해 보세요!',
            link=f'/partner/analytics',
            application=instance.application,
            extra_data={
                'event_id': instance.event.id,
                'event_name': event_name,
                'analytics_id': instance.id,
                'visitor_count': instance.visitor_count,
                'average_rating': float(instance.average_rating),
            }
        )

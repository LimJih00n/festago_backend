import requests
import secrets
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class SocialLoginMixin:
    """소셜 로그인 공통 기능"""

    def get_or_create_social_user(self, social_id, provider, email, nickname, profile_image=''):
        """소셜 사용자 조회 또는 생성"""
        # 기존 소셜 로그인 사용자 확인
        user = User.objects.filter(social_provider=provider, social_id=social_id).first()

        if user:
            # 기존 사용자: 프로필 이미지 업데이트
            if profile_image and user.profile_image != profile_image:
                user.profile_image = profile_image
                user.save(update_fields=['profile_image'])
            return user, False

        # 이메일로 기존 사용자 확인 (일반 가입 사용자)
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            # 기존 일반 가입 계정에 소셜 연동
            existing_user.social_provider = provider
            existing_user.social_id = social_id
            if profile_image:
                existing_user.profile_image = profile_image
            existing_user.save()
            return existing_user, False

        # 새 사용자 생성
        username = f"{provider}_{social_id}"
        user = User.objects.create(
            username=username,
            email=email,
            first_name=nickname,
            social_provider=provider,
            social_id=social_id,
            profile_image=profile_image,
            # 소셜 로그인 사용자는 비밀번호 불필요
            password=secrets.token_urlsafe(32)
        )
        return user, True

    def get_tokens_for_user(self, user):
        """JWT 토큰 생성"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def redirect_with_tokens(self, user):
        """프론트엔드로 토큰과 함께 리다이렉트"""
        tokens = self.get_tokens_for_user(user)
        frontend_url = settings.FRONTEND_URL.split(',')[0].strip()
        redirect_url = f"{frontend_url}/login/callback?access={tokens['access']}&refresh={tokens['refresh']}"
        return redirect(redirect_url)


# ==================== 카카오 로그인 ====================

class KakaoLoginView(APIView):
    """카카오 로그인 시작"""
    permission_classes = [AllowAny]

    def get(self, request):
        kakao_auth_url = (
            f"https://kauth.kakao.com/oauth/authorize"
            f"?client_id={settings.KAKAO_CLIENT_ID}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
            f"&response_type=code"
        )
        return redirect(kakao_auth_url)


class KakaoCallbackView(APIView, SocialLoginMixin):
    """카카오 로그인 콜백"""
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            return self._redirect_with_error('카카오 로그인이 취소되었습니다.')

        if not code:
            return self._redirect_with_error('인증 코드가 없습니다.')

        # 액세스 토큰 요청
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_CLIENT_ID,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'code': code,
        }
        # 클라이언트 시크릿이 설정된 경우 추가
        if settings.KAKAO_CLIENT_SECRET:
            token_data['client_secret'] = settings.KAKAO_CLIENT_SECRET

        token_response = requests.post(
            'https://kauth.kakao.com/oauth/token',
            data=token_data
        )

        if token_response.status_code != 200:
            return self._redirect_with_error('카카오 토큰 발급 실패')

        access_token = token_response.json().get('access_token')

        # 사용자 정보 요청
        user_response = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if user_response.status_code != 200:
            return self._redirect_with_error('카카오 사용자 정보 조회 실패')

        user_data = user_response.json()
        kakao_id = str(user_data.get('id'))
        kakao_account = user_data.get('kakao_account', {})
        profile = kakao_account.get('profile', {})

        email = kakao_account.get('email', f'kakao_{kakao_id}@festago.com')
        nickname = profile.get('nickname', '카카오 사용자')
        profile_image = profile.get('profile_image_url', '')

        user, created = self.get_or_create_social_user(
            social_id=kakao_id,
            provider='kakao',
            email=email,
            nickname=nickname,
            profile_image=profile_image
        )

        return self.redirect_with_tokens(user)

    def _redirect_with_error(self, message):
        frontend_url = settings.FRONTEND_URL.split(',')[0].strip()
        return redirect(f"{frontend_url}/login?error={message}")


# ==================== 네이버 로그인 ====================

class NaverLoginView(APIView):
    """네이버 로그인 시작"""
    permission_classes = [AllowAny]

    def get(self, request):
        state = secrets.token_urlsafe(16)
        naver_auth_url = (
            f"https://nid.naver.com/oauth2.0/authorize"
            f"?client_id={settings.NAVER_CLIENT_ID}"
            f"&redirect_uri={settings.NAVER_REDIRECT_URI}"
            f"&response_type=code"
            f"&state={state}"
        )
        return redirect(naver_auth_url)


class NaverCallbackView(APIView, SocialLoginMixin):
    """네이버 로그인 콜백"""
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            return self._redirect_with_error('네이버 로그인이 취소되었습니다.')

        if not code:
            return self._redirect_with_error('인증 코드가 없습니다.')

        # 액세스 토큰 요청
        token_response = requests.post(
            'https://nid.naver.com/oauth2.0/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': settings.NAVER_CLIENT_ID,
                'client_secret': settings.NAVER_CLIENT_SECRET,
                'code': code,
                'state': request.GET.get('state', ''),
            }
        )

        if token_response.status_code != 200:
            return self._redirect_with_error('네이버 토큰 발급 실패')

        access_token = token_response.json().get('access_token')

        # 사용자 정보 요청
        user_response = requests.get(
            'https://openapi.naver.com/v1/nid/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if user_response.status_code != 200:
            return self._redirect_with_error('네이버 사용자 정보 조회 실패')

        user_data = user_response.json().get('response', {})
        naver_id = user_data.get('id')
        email = user_data.get('email', f'naver_{naver_id}@festago.com')
        nickname = user_data.get('nickname') or user_data.get('name', '네이버 사용자')
        profile_image = user_data.get('profile_image', '')

        user, created = self.get_or_create_social_user(
            social_id=naver_id,
            provider='naver',
            email=email,
            nickname=nickname,
            profile_image=profile_image
        )

        return self.redirect_with_tokens(user)

    def _redirect_with_error(self, message):
        frontend_url = settings.FRONTEND_URL.split(',')[0].strip()
        return redirect(f"{frontend_url}/login?error={message}")


# ==================== 구글 로그인 ====================

class GoogleLoginView(APIView):
    """구글 로그인 시작"""
    permission_classes = [AllowAny]

    def get(self, request):
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=email%20profile"
        )
        return redirect(google_auth_url)


class GoogleCallbackView(APIView, SocialLoginMixin):
    """구글 로그인 콜백"""
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            return self._redirect_with_error('구글 로그인이 취소되었습니다.')

        if not code:
            return self._redirect_with_error('인증 코드가 없습니다.')

        # 액세스 토큰 요청
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                'code': code,
            }
        )

        if token_response.status_code != 200:
            return self._redirect_with_error('구글 토큰 발급 실패')

        access_token = token_response.json().get('access_token')

        # 사용자 정보 요청
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if user_response.status_code != 200:
            return self._redirect_with_error('구글 사용자 정보 조회 실패')

        user_data = user_response.json()
        google_id = user_data.get('id')
        email = user_data.get('email', f'google_{google_id}@festago.com')
        nickname = user_data.get('name', '구글 사용자')
        profile_image = user_data.get('picture', '')

        user, created = self.get_or_create_social_user(
            social_id=google_id,
            provider='google',
            email=email,
            nickname=nickname,
            profile_image=profile_image
        )

        return self.redirect_with_tokens(user)

    def _redirect_with_error(self, message):
        frontend_url = settings.FRONTEND_URL.split(',')[0].strip()
        return redirect(f"{frontend_url}/login?error={message}")

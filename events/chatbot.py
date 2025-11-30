"""
OpenAI GPT 기반 축제 추천 챗봇 API
"""
import json
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from openai import OpenAI
from .models import Event


class ChatbotView(APIView):
    """GPT 기반 축제 추천 챗봇"""
    permission_classes = [AllowAny]

    def get_events_context(self):
        """축제 데이터를 GPT 컨텍스트로 변환"""
        events = Event.objects.all()[:50]  # 최대 50개

        events_list = []
        for event in events:
            events_list.append({
                'id': event.id,
                'name': event.name,
                'category': event.category,
                'location': event.location,
                'start_date': str(event.start_date) if event.start_date else None,
                'end_date': str(event.end_date) if event.end_date else None,
                'description': event.description[:200] if event.description else None,
            })

        return json.dumps(events_list, ensure_ascii=False)

    def get_system_prompt(self, events_context):
        """시스템 프롬프트 생성"""
        return f"""당신은 친절하고 유쾌한 축제 추천 AI 어시스턴트 '페스타고'입니다.

## 역할
- 사용자에게 맞춤형 축제, 공연, 전시, 팝업스토어를 추천합니다.
- 친근하고 재미있게 대화하며, 이모지를 적절히 사용합니다.
- 한국어로 대화합니다.

## 축제 데이터
현재 진행 중이거나 예정된 행사 목록입니다:
{events_context}

## 응답 규칙
1. 사용자의 취향, 위치, 날짜 등을 파악하여 적절한 행사를 추천하세요.
2. 추천할 때는 행사 이름, 장소, 날짜를 포함하세요.
3. 추천 행사가 있을 경우, 응답 마지막에 다음 JSON 형식을 포함하세요:
   [RECOMMENDATIONS]
   {{"event_ids": [1, 2, 3]}}
   [/RECOMMENDATIONS]
4. 추천할 행사가 없거나 일반 대화인 경우 JSON을 포함하지 마세요.
5. 응답은 자연스럽고 대화체로 작성하세요.
6. 카테고리: festival(축제), concert(공연), exhibition(전시), popup(팝업스토어)

## 예시 응답
"서울에서 이번 주말에 가기 좋은 축제를 찾고 계시군요! 🎉

제가 추천드리는 축제는:
1. **한강 페스티벌** - 한강공원, 12/1~12/3
2. **서울 빛초롱축제** - 청계천, 12/1~12/15

둘 다 서울 중심에서 열려서 접근성이 좋아요! 어떤 게 마음에 드세요?

[RECOMMENDATIONS]
{{"event_ids": [1, 5]}}
[/RECOMMENDATIONS]"
"""

    def post(self, request):
        """채팅 메시지 처리"""
        messages = request.data.get('messages', [])

        if not messages:
            return Response(
                {'error': '메시지가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OpenAI API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return Response(
                {'error': 'OpenAI API 키가 설정되지 않았습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # OpenAI 클라이언트 생성
            client = OpenAI(api_key=api_key)

            # 축제 데이터 컨텍스트 가져오기
            events_context = self.get_events_context()
            system_prompt = self.get_system_prompt(events_context)

            # GPT API 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 비용 효율적인 모델
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            assistant_message = response.choices[0].message.content

            # 추천 이벤트 ID 추출
            recommended_events = []
            if '[RECOMMENDATIONS]' in assistant_message:
                try:
                    start = assistant_message.index('[RECOMMENDATIONS]') + len('[RECOMMENDATIONS]')
                    end = assistant_message.index('[/RECOMMENDATIONS]')
                    json_str = assistant_message[start:end].strip()
                    rec_data = json.loads(json_str)
                    event_ids = rec_data.get('event_ids', [])

                    # 이벤트 정보 가져오기
                    events = Event.objects.filter(id__in=event_ids)
                    for event in events:
                        recommended_events.append({
                            'id': event.id,
                            'name': event.name,
                            'category': event.category,
                            'location': event.location,
                            'start_date': str(event.start_date) if event.start_date else None,
                            'end_date': str(event.end_date) if event.end_date else None,
                            'poster_image': event.poster_image if event.poster_image else None,
                        })

                    # 응답에서 JSON 부분 제거
                    assistant_message = assistant_message[:assistant_message.index('[RECOMMENDATIONS]')].strip()
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"추천 파싱 오류: {e}")

            return Response({
                'message': assistant_message,
                'recommendations': recommended_events,
            })

        except Exception as e:
            print(f"챗봇 오류: {e}")
            return Response(
                {'error': f'챗봇 처리 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

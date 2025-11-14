"""
이미지 처리 유틸리티 함수
"""
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def resize_image(image_file, max_width=1920, max_height=1080, quality=85):
    """
    이미지 리사이징 함수

    Args:
        image_file: Django UploadedFile 객체
        max_width: 최대 너비 (기본: 1920px)
        max_height: 최대 높이 (기본: 1080px)
        quality: JPEG 품질 (기본: 85)

    Returns:
        리사이징된 InMemoryUploadedFile 객체
    """
    try:
        # 이미지 열기
        img = Image.open(image_file)

        # EXIF orientation 처리 (회전 정보)
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # 원본 크기
        original_width, original_height = img.size

        # 리사이징 필요 여부 확인
        if original_width <= max_width and original_height <= max_height:
            return image_file  # 리사이징 불필요

        # 비율 유지하며 리사이징
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # RGB 모드로 변환 (RGBA나 P 모드는 JPEG로 저장 불가)
        if img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # BytesIO에 저장
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        # 새 파일명 생성 (확장자를 .jpg로 변경)
        original_name = image_file.name
        name_parts = original_name.rsplit('.', 1)
        new_name = name_parts[0] + '.jpg'

        # InMemoryUploadedFile 객체 생성
        resized_file = InMemoryUploadedFile(
            output,
            'ImageField',
            new_name,
            'image/jpeg',
            sys.getsizeof(output),
            None
        )

        return resized_file

    except Exception as e:
        # 리사이징 실패 시 원본 반환
        print(f"이미지 리사이징 실패: {str(e)}")
        return image_file


def create_thumbnail(image_file, size=(300, 300)):
    """
    썸네일 생성 함수

    Args:
        image_file: Django UploadedFile 객체
        size: 썸네일 크기 (기본: 300x300)

    Returns:
        썸네일 InMemoryUploadedFile 객체
    """
    try:
        img = Image.open(image_file)

        # EXIF orientation 처리
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # 정사각형 크롭 후 리사이징
        width, height = img.size
        min_dimension = min(width, height)

        # 중앙 크롭
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension

        img = img.crop((left, top, right, bottom))
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # RGB 모드로 변환
        if img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # BytesIO에 저장
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)

        # 새 파일명 생성
        original_name = image_file.name
        name_parts = original_name.rsplit('.', 1)
        new_name = name_parts[0] + '_thumb.jpg'

        # InMemoryUploadedFile 객체 생성
        thumbnail_file = InMemoryUploadedFile(
            output,
            'ImageField',
            new_name,
            'image/jpeg',
            sys.getsizeof(output),
            None
        )

        return thumbnail_file

    except Exception as e:
        print(f"썸네일 생성 실패: {str(e)}")
        return None

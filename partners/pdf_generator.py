"""
PDF 리포트 생성 유틸리티
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os


def get_korean_style():
    """한글 지원 스타일 반환"""
    styles = getSampleStyleSheet()

    # 한글 폰트 등록 시도 (시스템에 있는 경우)
    try:
        # Windows
        if os.path.exists('C:/Windows/Fonts/malgun.ttf'):
            pdfmetrics.registerFont(TTFont('Korean', 'C:/Windows/Fonts/malgun.ttf'))
            font_name = 'Korean'
        else:
            font_name = 'Helvetica'
    except:
        font_name = 'Helvetica'

    # 커스텀 스타일 생성
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=6,
    )

    return {
        'title': title_style,
        'heading': heading_style,
        'body': body_style,
    }


def generate_analytics_pdf(analytics_data, partner_name, event_name):
    """
    성과 데이터 PDF 리포트 생성

    Args:
        analytics_data: AnalyticsData 모델 인스턴스
        partner_name: 사업자명
        event_name: 이벤트명

    Returns:
        BytesIO: PDF 파일 데이터
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # 스타일
    styles = get_korean_style()

    # 컨텐츠 생성
    story = []

    # === 제목 ===
    title = Paragraph(f"Performance Report", styles['title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # === 기본 정보 ===
    info_data = [
        ['Partner:', partner_name],
        ['Event:', event_name],
        ['Date:', analytics_data.generated_at.strftime('%Y-%m-%d')],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a1a1a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # === 핵심 지표 ===
    story.append(Paragraph("Key Performance Indicators", styles['heading']))

    kpi_data = [
        ['Metric', 'Value'],
        ['Visitor Count', f"{analytics_data.visitor_count:,}"],
        ['Estimated Sales', f"{analytics_data.estimated_sales:,.0f} KRW"],
        ['Average Rating', f"{analytics_data.average_rating:.1f} / 5.0"],
        ['Review Count', f"{analytics_data.review_count:,}"],
        ['Sentiment Score', f"{analytics_data.sentiment_score:.1f}%"],
    ]

    kpi_table = Table(kpi_data, colWidths=[3*inch, 3*inch])
    kpi_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 20))

    # === 인기 제품 ===
    if analytics_data.top_products:
        story.append(Paragraph("Top Products", styles['heading']))

        product_data = [['Rank', 'Product Name', 'Sales', 'Revenue']]
        for product in analytics_data.top_products[:5]:
            product_data.append([
                str(product.get('rank', '-')),
                product.get('name', 'N/A'),
                str(product.get('sales', 0)),
                f"{product.get('revenue', 0):,.0f} KRW"
            ])

        product_table = Table(product_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.5*inch])
        product_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(product_table)
        story.append(Spacer(1, 20))

    # === 시간대별 방문객 ===
    if analytics_data.hourly_visitors:
        story.append(Paragraph("Hourly Visitor Distribution", styles['heading']))

        hourly_data = [['Hour', 'Visitors']]
        for hour, count in sorted(analytics_data.hourly_visitors.items()):
            hourly_data.append([f"{hour}:00", str(count)])

        hourly_table = Table(hourly_data, colWidths=[1.5*inch, 1.5*inch])
        hourly_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(hourly_table)
        story.append(Spacer(1, 20))

    # === 리뷰 분석 ===
    story.append(Paragraph("Review Analysis", styles['heading']))

    # 긍정 키워드
    if analytics_data.positive_keywords:
        story.append(Paragraph("Positive Keywords:", styles['body']))
        positive_text = ", ".join([f"{kw['word']} ({kw['count']})" for kw in analytics_data.positive_keywords[:10]])
        story.append(Paragraph(positive_text, styles['body']))
        story.append(Spacer(1, 10))

    # 부정 키워드
    if analytics_data.negative_keywords:
        story.append(Paragraph("Negative Keywords:", styles['body']))
        negative_text = ", ".join([f"{kw['word']} ({kw['count']})" for kw in analytics_data.negative_keywords[:10]])
        story.append(Paragraph(negative_text, styles['body']))
        story.append(Spacer(1, 20))

    # === 푸터 ===
    footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Powered by Festago"
    footer = Paragraph(footer_text, styles['body'])
    story.append(Spacer(1, 30))
    story.append(footer)

    # PDF 생성
    doc.build(story)
    buffer.seek(0)
    return buffer

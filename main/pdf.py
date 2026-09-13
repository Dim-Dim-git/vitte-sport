"""Формирование программы тренировок в формате PDF."""
import io
import os

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer
from svglib.fonts import get_global_font_map
from svglib.svglib import svg2rlg

# Цвета портала
RED  = colors.HexColor('#C21631')
DARK = colors.HexColor('#132041')
GREY = colors.HexColor('#4F6A84')

FONTS_REGISTERED = False


# Подключение шрифта с поддержкой кириллицы
def register_fonts():
    global FONTS_REGISTERED
    if FONTS_REGISTERED:
        return

    fonts_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    regular  = os.path.join(fonts_dir, 'Montserrat-Regular.ttf')
    semibold = os.path.join(fonts_dir, 'Montserrat-SemiBold.ttf')

    pdfmetrics.registerFont(TTFont('Montserrat', regular))
    pdfmetrics.registerFont(TTFont('Montserrat-Bold', semibold))
    get_global_font_map().register_font_family('Montserrat', normal=regular, bold=semibold)
    # в SVG вес может быть числом, для svglib это отдельное значение
    get_global_font_map().register_font(
        'Montserrat', semibold, weight='600', rlgFontName='Montserrat-Bold')

    FONTS_REGISTERED = True


# Оформление заголовков и текста документа
def build_styles():
    return {
        'title':   ParagraphStyle('title', fontName='Montserrat-Bold', fontSize=20,
                                  leading=26, textColor=DARK, spaceAfter=4),
        'sub':     ParagraphStyle('sub', fontName='Montserrat', fontSize=11,
                                  leading=15, textColor=GREY, spaceAfter=16),
        'session': ParagraphStyle('session', fontName='Montserrat-Bold', fontSize=14,
                                  leading=18, textColor=RED, spaceBefore=14, spaceAfter=8),
        'block':   ParagraphStyle('block', fontName='Montserrat-Bold', fontSize=12,
                                  leading=16, textColor=DARK, spaceAfter=2),
        'meta':    ParagraphStyle('meta', fontName='Montserrat', fontSize=9,
                                  leading=12, textColor=GREY, spaceAfter=6),
        'text':    ParagraphStyle('text', fontName='Montserrat', fontSize=10,
                                  leading=14, textColor=DARK, spaceAfter=8),
    }


# Схема блока из статики, вписанная в ширину страницы
def scheme_drawing(scheme, max_width):
    if not scheme:
        return None

    path = os.path.join(settings.BASE_DIR, 'static', scheme.replace('/', os.sep))
    if not os.path.exists(path):
        return None

    try:
        drawing = svg2rlg(path)
    except Exception:
        return None

    if drawing is None or not drawing.width:
        return None

    k = min(max_width / drawing.width, 1)
    drawing.width  *= k
    drawing.height *= k
    drawing.scale(k, k)
    return drawing


# Сборка документа: описание программы, занятия, блоки со схемами
def build_program_pdf(program, sessions):
    register_fonts()
    styles = build_styles()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=program.title, author='Спортивный портал МУИВ',
    )
    content_width = doc.width

    story = [
        Paragraph(program.title, styles['title']),
        Paragraph(f'Секция: {program.sport.name}', styles['sub']),
        Paragraph(program.description.replace('\n', '<br/>'), styles['text']),
    ]

    for session, items in sessions:
        heading = [Paragraph(f'Занятие {session}', styles['session'])]

        for number, item in enumerate(items, start=1):
            block = item.block
            meta = [block.get_kind_display(), f'{block.duration_min} мин']
            if block.equipment:
                meta.append(block.equipment)

            part = [
                Paragraph(f'{number}. {block.title}', styles['block']),
                Paragraph(' · '.join(meta), styles['meta']),
                Paragraph(block.description.replace('\n', '<br/>'), styles['text']),
            ]

            drawing = scheme_drawing(block.scheme, content_width)
            if drawing is not None:
                part.append(drawing)
                part.append(Spacer(1, 8 * mm))

            # заголовок занятия печатается вместе с первым блоком
            story.append(KeepTogether(heading + part))
            heading = []

    # Колонтитул с номером страницы
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont('Montserrat', 8)
        canvas.setFillColor(GREY)
        canvas.drawCentredString(
            A4[0] / 2, 10 * mm,
            f'Спортивный портал МУИВ им. С.Ю. Витте  ·  страница {document.page}')
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
"""
SocialImageGenerator — Pillow tabanli gorsel sablon motoru.

3 temel sablon:
  1. info_card   — Bilgi kartlari (tip, istatistik, bilgilendirme)
  2. stat_card   — Istatistik gosterim (buyuk rakam + aciklama)
  3. quote_card  — Alinti / motivasyon kartlari

Norosera brand:
  Primary: #1B4F72 (koyu mavi)
  Secondary: #00BCD4 (turkuaz)
  Accent: #F39C12 (turuncu)
  Background: #F8FAFC (acik gri)
  Text: #2C3E50 (koyu gri)
"""

import os
import io
import math
import logging
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# ============================================================================
# Renkler (Norosera Brand)
# ============================================================================

COLORS = {
    'primary': '#1B4F72',
    'secondary': '#00BCD4',
    'accent': '#F39C12',
    'bg_light': '#F8FAFC',
    'bg_white': '#FFFFFF',
    'text_dark': '#2C3E50',
    'text_light': '#FFFFFF',
    'text_muted': '#7F8C8D',
    'gradient_start': '#1B4F72',
    'gradient_end': '#2980B9',
    'success': '#27AE60',
    'warning': '#F39C12',
    'danger': '#E74C3C',
}

# ============================================================================
# Boyutlar
# ============================================================================

SIZES = {
    'instagram_square': (1080, 1080),
    'instagram_portrait': (1080, 1350),
    'instagram_story': (1080, 1920),
    'linkedin_landscape': (1200, 627),
    'linkedin_square': (1080, 1080),
}

# ============================================================================
# Font dosya yolu
# ============================================================================

FONT_DIR = Path(__file__).parent / 'fonts'


def _hex_to_rgb(hex_color: str) -> tuple:
    """Hex renk kodunu RGB tuple'a cevir."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Font yukle. Yoksa default kullan."""
    if bold:
        font_names = ['Inter-Bold.ttf', 'Roboto-Bold.ttf', 'NotoSans-Bold.ttf']
    else:
        font_names = ['Inter-Regular.ttf', 'Roboto-Regular.ttf', 'NotoSans-Regular.ttf']

    for name in font_names:
        font_path = FONT_DIR / name
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                continue

    # Fallback: Pillow default
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Metni satir satir kes (word-wrap)."""
    words = text.split()
    lines = []
    current = ''

    for word in words:
        test = f'{current} {word}'.strip()
        bbox = font.getbbox(test)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines or ['']


def _draw_rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int, fill: str):
    """Yuvarlatilmis dikdortgen ciz."""
    x0, y0, x1, y1 = xy
    fill_rgb = _hex_to_rgb(fill) if isinstance(fill, str) and fill.startswith('#') else fill

    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill_rgb)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill_rgb)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill_rgb)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill_rgb)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill_rgb)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill_rgb)


class SocialImageGenerator:
    """
    Sosyal medya icin gorsel ureten sinif.

    Kullanim:
        gen = SocialImageGenerator()
        img_bytes = gen.info_card(
            title='Migren Tetikleyicileri',
            items=['Stres', 'Uyku bozuklugu', 'Dehidrasyon'],
            platform='instagram',
        )
    """

    def __init__(self):
        self.colors = COLORS
        self.sizes = SIZES

    def _create_canvas(self, platform: str, bg_color: str = None) -> tuple:
        """Platform'a gore bos canvas olustur."""
        size_key = f'{platform}_square'
        if size_key not in self.sizes:
            size_key = 'instagram_square'

        width, height = self.sizes[size_key]
        bg = _hex_to_rgb(bg_color or self.colors['bg_light'])
        img = Image.new('RGB', (width, height), bg)
        draw = ImageDraw.Draw(img)
        return img, draw, width, height

    def _add_brand_bar(self, draw: ImageDraw.Draw, width: int, height: int):
        """Alt kisma Norosera brand bar ekle."""
        bar_h = 80
        y_start = height - bar_h

        # Brand bar arkaplan
        draw.rectangle([0, y_start, width, height], fill=_hex_to_rgb(self.colors['primary']))

        # Logo text
        font = _get_font(28, bold=True)
        text = 'NOROSERA'
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        draw.text((x, y_start + 25), text, fill=_hex_to_rgb(self.colors['text_light']), font=font)

    def _add_top_accent(self, draw: ImageDraw.Draw, width: int):
        """Ust kisma ince accent cizgi."""
        draw.rectangle([0, 0, width, 8], fill=_hex_to_rgb(self.colors['secondary']))

    def _to_bytes(self, img: Image.Image, format: str = 'PNG') -> bytes:
        """Image'i bytes olarak dondur."""
        buf = io.BytesIO()
        img.save(buf, format=format, quality=95)
        buf.seek(0)
        return buf.getvalue()

    # ========================================================================
    # 1) INFO CARD
    # ========================================================================

    def info_card(
        self,
        title: str,
        items: list,
        platform: str = 'instagram',
        subtitle: str = '',
        bg_color: str = None,
        accent_color: str = None,
        icon_emoji: str = '',
    ) -> bytes:
        """
        Bilgi karti sablonu.
        Baslik + madde listesi.

        Args:
            title: Ana baslik
            items: Maddeler listesi (str)
            platform: instagram | linkedin
            subtitle: Alt baslik (opsiyonel)
            bg_color: Arkaplan rengi
            accent_color: Vurgu rengi
            icon_emoji: Madde basi ikonu

        Returns:
            PNG bytes
        """
        img, draw, w, h = self._create_canvas(platform, bg_color)
        accent = accent_color or self.colors['secondary']

        # Ust accent
        self._add_top_accent(draw, w)

        # Baslik alani arkaplan
        header_h = 220
        draw.rectangle([0, 8, w, header_h], fill=_hex_to_rgb(self.colors['primary']))

        # Baslik
        title_font = _get_font(52, bold=True)
        title_lines = _wrap_text(title, title_font, w - 120)
        y = 40
        for line in title_lines[:3]:
            draw.text((60, y), line, fill=_hex_to_rgb(self.colors['text_light']), font=title_font)
            y += 62

        # Subtitle
        if subtitle:
            sub_font = _get_font(28)
            draw.text((60, y + 5), subtitle, fill=_hex_to_rgb('#AED6F1'), font=sub_font)

        # Maddeler
        item_font = _get_font(36)
        number_font = _get_font(36, bold=True)
        y = header_h + 50
        max_items = min(len(items), 7)  # Max 7 madde

        for i, item in enumerate(items[:max_items]):
            # Numara dairesi
            circle_x = 80
            circle_r = 24
            _draw_rounded_rect(draw, (circle_x - circle_r, y - 5, circle_x + circle_r, y + 43), 24, accent)

            # Numara
            num = str(i + 1)
            num_bbox = number_font.getbbox(num)
            num_w = num_bbox[2] - num_bbox[0]
            draw.text(
                (circle_x - num_w // 2, y),
                num,
                fill=_hex_to_rgb(self.colors['text_light']),
                font=number_font,
            )

            # Madde metni
            prefix = f'{icon_emoji} ' if icon_emoji else ''
            text_lines = _wrap_text(f'{prefix}{item}', item_font, w - 200)
            for tl in text_lines[:2]:
                draw.text((130, y), tl, fill=_hex_to_rgb(self.colors['text_dark']), font=item_font)
                y += 44
            y += 20

        # Brand bar
        self._add_brand_bar(draw, w, h)

        return self._to_bytes(img)

    # ========================================================================
    # 2) STAT CARD
    # ========================================================================

    def stat_card(
        self,
        stat_value: str,
        stat_label: str,
        description: str = '',
        platform: str = 'instagram',
        bg_color: str = None,
        stat_color: str = None,
        source: str = '',
    ) -> bytes:
        """
        Istatistik karti sablonu.
        Buyuk rakam + aciklama.

        Args:
            stat_value: Buyuk gosterilecek rakam/deger (ör: '%80', '3x', '1/4')
            stat_label: Rakamin kisa aciklamasi
            description: Detayli aciklama
            platform: instagram | linkedin
            bg_color: Arkaplan rengi
            stat_color: Rakam rengi
            source: Kaynak bilgisi

        Returns:
            PNG bytes
        """
        img, draw, w, h = self._create_canvas(platform, bg_color)
        s_color = stat_color or self.colors['secondary']

        # Ust accent
        self._add_top_accent(draw, w)

        # Buyuk deger
        stat_font = _get_font(160, bold=True)
        stat_bbox = stat_font.getbbox(stat_value)
        stat_w = stat_bbox[2] - stat_bbox[0]
        stat_x = (w - stat_w) // 2
        stat_y = h // 2 - 200

        draw.text((stat_x, stat_y), stat_value, fill=_hex_to_rgb(s_color), font=stat_font)

        # Ince ayirici cizgi
        line_y = stat_y + 190
        line_w = 120
        draw.rectangle(
            [(w - line_w) // 2, line_y, (w + line_w) // 2, line_y + 4],
            fill=_hex_to_rgb(self.colors['accent']),
        )

        # Label
        label_font = _get_font(42, bold=True)
        label_lines = _wrap_text(stat_label, label_font, w - 160)
        y = line_y + 30
        for line in label_lines[:2]:
            lbbox = label_font.getbbox(line)
            lw = lbbox[2] - lbbox[0]
            draw.text(((w - lw) // 2, y), line, fill=_hex_to_rgb(self.colors['text_dark']), font=label_font)
            y += 52

        # Aciklama
        if description:
            desc_font = _get_font(28)
            desc_lines = _wrap_text(description, desc_font, w - 160)
            y += 20
            for line in desc_lines[:3]:
                dbbox = desc_font.getbbox(line)
                dw = dbbox[2] - dbbox[0]
                draw.text(((w - dw) // 2, y), line, fill=_hex_to_rgb(self.colors['text_muted']), font=desc_font)
                y += 36

        # Kaynak
        if source:
            src_font = _get_font(20)
            draw.text((60, h - 110), f'Kaynak: {source}', fill=_hex_to_rgb(self.colors['text_muted']), font=src_font)

        # Brand bar
        self._add_brand_bar(draw, w, h)

        return self._to_bytes(img)

    # ========================================================================
    # 3) QUOTE CARD
    # ========================================================================

    def quote_card(
        self,
        quote: str,
        author: str = '',
        platform: str = 'instagram',
        bg_color: str = None,
        quote_color: str = None,
    ) -> bytes:
        """
        Alinti / motivasyon karti sablonu.

        Args:
            quote: Alinti metni
            author: Yazar (opsiyonel)
            platform: instagram | linkedin
            bg_color: Arkaplan rengi
            quote_color: Alinti metni rengi

        Returns:
            PNG bytes
        """
        bg = bg_color or self.colors['primary']
        img, draw, w, h = self._create_canvas(platform, bg)
        q_color = quote_color or self.colors['text_light']

        # Buyuk tirnak isareti
        quote_mark_font = _get_font(200, bold=True)
        draw.text(
            (60, 60),
            '\u201C',
            fill=_hex_to_rgb(self.colors['secondary']),
            font=quote_mark_font,
        )

        # Alinti metni
        quote_font = _get_font(44, bold=True)
        lines = _wrap_text(quote, quote_font, w - 160)
        y = 280
        for line in lines[:8]:
            draw.text((80, y), line, fill=_hex_to_rgb(q_color), font=quote_font)
            y += 56

        # Kapatis tirnak
        draw.text(
            (w - 180, y + 10),
            '\u201D',
            fill=_hex_to_rgb(self.colors['secondary']),
            font=quote_mark_font,
        )

        # Yazar
        if author:
            author_font = _get_font(30)
            author_text = f'\u2014 {author}'
            draw.text((80, y + 80), author_text, fill=_hex_to_rgb(self.colors['accent']), font=author_font)

        # Alt ince cizgi
        draw.rectangle([60, h - 120, w - 60, h - 116], fill=_hex_to_rgb(self.colors['secondary']))

        # Brand bar (koyu arka plan icin beyaz)
        bar_h = 80
        y_start = h - bar_h
        draw.rectangle([0, y_start, w, h], fill=_hex_to_rgb(self.colors['bg_white']))

        font = _get_font(28, bold=True)
        text = 'NOROSERA'
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        draw.text((x, y_start + 25), text, fill=_hex_to_rgb(self.colors['primary']), font=font)

        return self._to_bytes(img)

    # ========================================================================
    # UTILITY: Generate from visual brief
    # ========================================================================

    def generate_from_brief(self, brief: dict, platform: str = 'instagram') -> Optional[bytes]:
        """
        Visual brief'den otomatik gorsel uret.
        Brief'teki template_type'a gore uygun sablonu sec.

        Args:
            brief: Visual brief dict
            platform: instagram | linkedin

        Returns:
            PNG bytes veya None (hata durumunda)
        """
        try:
            template_type = brief.get('template_type', 'info_card')

            if template_type == 'stat_card':
                return self.stat_card(
                    stat_value=brief.get('stat_value', ''),
                    stat_label=brief.get('stat_label', ''),
                    description=brief.get('description', ''),
                    platform=platform,
                    source=brief.get('source', ''),
                )
            elif template_type == 'quote_card':
                return self.quote_card(
                    quote=brief.get('quote', ''),
                    author=brief.get('author', ''),
                    platform=platform,
                )
            else:
                # Default: info_card
                return self.info_card(
                    title=brief.get('title', ''),
                    items=brief.get('items', []),
                    platform=platform,
                    subtitle=brief.get('subtitle', ''),
                )
        except Exception as e:
            logger.error(f'Image generation error: {e}')
            return None

    def get_available_sizes(self) -> dict:
        """Mevcut platform boyutlarini dondur."""
        return dict(self.sizes)

    def get_available_templates(self) -> list:
        """Mevcut sablon turlerini dondur."""
        return [
            {
                'name': 'info_card',
                'label': 'Bilgi Karti',
                'description': 'Baslik + maddeler listesi',
                'required_fields': ['title', 'items'],
            },
            {
                'name': 'stat_card',
                'label': 'Istatistik Karti',
                'description': 'Buyuk rakam + aciklama',
                'required_fields': ['stat_value', 'stat_label'],
            },
            {
                'name': 'quote_card',
                'label': 'Alinti Karti',
                'description': 'Motivasyon / alinti metni',
                'required_fields': ['quote'],
            },
        ]

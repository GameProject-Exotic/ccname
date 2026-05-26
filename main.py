from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from pathlib import Path


_RES_PATH = Path(__file__).parent / 'res'
_RES_RANKS_PATH = _RES_PATH / 'ranks'
_RES_RANKS_TRIKZ_PATH = _RES_RANKS_PATH / 'trikz'
_RES_RANKS_BHOP_PATH = _RES_RANKS_PATH / 'bhop'
_RES_FONTS_PATH = _RES_PATH / 'fonts'
_RES_RANK_FONT_PATH = _RES_FONTS_PATH / 'opificio.ttf'

_TRIKZ_RANKS = {
    'Newbie': ('#a1887f', '#d7ccc8'),
    'Bronze': ('#4a2c0e', '#cd7f32'),
    'Silver': ('#4a4b53', '#c0c0c0'),
    'Gold': ('#784a0b', '#fbbf24'),
    'Peridot': ('#3b5c1e', '#a3e635'),
    'Lapis': ('#2e1a5e', '#6366f1'),
    'Emerald': ('#064e3b', '#10b981'),
    'Ruby': ('#7f1d1d', '#ef4444'),
    'Sapphire': ('#0f172a', '#1d4ed8'),
    'Diamond': ('#3b82f6', '#bae6fd'),
    'Expert': ('#4a3b52', '#b8a9c6'),
    'Master': ('#2e1065', '#a855f7'),
    'Legend': ('#b91c1c', '#fcd34d'),
    'Eternal': ('#be185d', '#f472b6')
}

_TRIKZ_RANK_IMAGE_WIDTH = 2048
_TRIKZ_RANK_IMAGE_HEIGHT = 2048
_TRIKZ_RANK_IMAGE_PADDING = int(24 * (_TRIKZ_RANK_IMAGE_WIDTH / 2048))

_RANK_TEXT_FONT_MAX_SIZE = 512
_RANK_TEXT_STROKE_WIDTH = int(12 * (_TRIKZ_RANK_IMAGE_WIDTH / 2048))
_RANK_TEXT_OUTLINE_WIDTH = 1
_RANK_TEXT_OUTLINE_FACTOR = 0.52


def _hex2rgb(hex_):
    hex_ = hex_.lstrip('#')

    if len(hex_) == 3:
        hex_ = ''.join([c*2 for c in hex_])

    return tuple(int(hex_[i:i+2], 16) for i in (0, 2, 4))


def _fontsz(text, path, size):
    font = ImageFont.truetype(path, size)

    image = Image.new('RGBA', (1, 1), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    return width, height, font


def _find_font(width, height, padding, text, path, size):
    max_text_width = width - padding * 2
    max_text_height = height - padding * 2

    result_size = 1

    low, high = 1, size
    while low <= high:
        mid = (low + high) // 2

        text_width, text_height, font = _fontsz(text, path, mid)
        if text_width <= max_text_width \
                and text_height <= max_text_height:
            result_size = mid
            low = mid + 1
        else:
            high = mid - 1

    text_width, text_height, result_font = _fontsz(text, path, result_size)

    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    return text_x, text_y, text_width, text_height, result_size, result_font



def _main():
    longest_rank = max(_TRIKZ_RANKS.keys(), key=len)
    _, _, _, _, m_font_sz, _ = _find_font(_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT, _TRIKZ_RANK_IMAGE_PADDING, longest_rank, _RES_RANK_FONT_PATH, _RANK_TEXT_FONT_MAX_SIZE)

    for rank, hexs in _TRIKZ_RANKS.items():
        color0 = _hex2rgb(hexs[0])
        color1 = _hex2rgb(hexs[-1])

        text_image = Image.new('RGBA', (_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_image)

        outline_image = Image.new('RGBA', (_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT), (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline_image)

        x, y, _, _, _, font = _find_font(_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT, _TRIKZ_RANK_IMAGE_PADDING, rank, _RES_RANK_FONT_PATH, m_font_sz)

        outline_draw.text((x, y), rank, font=font, fill=(255, 255, 255, 255), stroke_width=_RANK_TEXT_OUTLINE_WIDTH, stroke_fill=(0, 0, 0, 255))
        text_draw.text((x, y), rank, font=font, fill=(255, 255, 255, 255))

        text_gradient = Image.new('RGBA', (_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT), (0, 0, 0, 0))
        outline_gradient = Image.new('RGBA', (_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT), (0, 0, 0, 0))
        for i in range(_TRIKZ_RANK_IMAGE_WIDTH):
            for j in range(_TRIKZ_RANK_IMAGE_HEIGHT):
                ratio = i / _TRIKZ_RANK_IMAGE_WIDTH
                ratio = max(0, min(1, ratio))

                r = int(color0[0] * (1 - ratio) + color1[0] * ratio)
                g = int(color0[1] * (1 - ratio) + color1[1] * ratio)
                b = int(color0[2] * (1 - ratio) + color1[2] * ratio)

                dr = int(r * _RANK_TEXT_OUTLINE_FACTOR)
                dg = int(g * _RANK_TEXT_OUTLINE_FACTOR)
                db = int(b * _RANK_TEXT_OUTLINE_FACTOR)

                text_gradient.putpixel((i, j), (r, g, b, 255))
                outline_gradient.putpixel((i, j), (dr, dg, db, 255))

        text_mask = text_image.split()[3]
        outline_mask = outline_image.split()[3]

        result_text_image = Image.new('RGBA', (_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT), (0, 0, 0, 0))
        result_text_image.paste(text_gradient, (0, 0), mask=text_mask)

        result_outline_image = Image.new('RGBA', (_TRIKZ_RANK_IMAGE_WIDTH, _TRIKZ_RANK_IMAGE_HEIGHT), (0, 0, 0, 0))
        result_outline_image.paste(outline_gradient, (0, 0), mask=outline_mask)

        result_image = Image.alpha_composite(result_outline_image, result_text_image)
        result_image.save(_RES_RANKS_TRIKZ_PATH / f'{rank}~{_TRIKZ_RANK_IMAGE_WIDTH}x{_TRIKZ_RANK_IMAGE_HEIGHT}.png')


if __name__ == '__main__':
    _main()

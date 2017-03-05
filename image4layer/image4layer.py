#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Image4Layer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: Copyright 2007-2017 Toshiyuki Ishii.
    :license: MIT, see LICENSE for details.
"""
# noinspection PyPackageRequirements
from PIL import Image, ImageMath  # noqa
from itertools import zip_longest


class Image4Layer(object):
    __version__ = "0.41"

    @staticmethod
    def normal(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="b")

    @staticmethod
    def overlay(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _overlay)

    @staticmethod
    def soft_light(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _soft_light)

    @staticmethod
    def hard_light(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _hard_light)

    @staticmethod
    def linear_light(cb, cs):
        """
        base + 2 * ref - 1      | if ref < 0.5
        base + 2 * (ref - 0.5)  | otherwise

        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _linear_light)

    @staticmethod
    def exclusion(cb, cs):
        """
        base + ref - (2 * base * ref)

        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _exclusion)

    @staticmethod
    def color_burn(cb, cs):
        """
        1 - (1 - base) / ref

        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _color_burn)

    @staticmethod
    def color_dodge(cb, cs):
        """
        base / (1 - ref)

        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _color_dodge)

    @staticmethod
    def pin_light(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(
            cb, cs,
            eval_str="min(a, 2 * b) * (b < 128) + max(a, 2 * (b - 128)) * (b >= 128)"
        )

    @staticmethod
    def vivid_light(cb, cs):
        """
        1 - (1 - base) / (2 * ref)    | if ref < 0.5
        base / (1 - 2 * (ref - 0.5))  | otherwise

        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _vivid_light)

    @staticmethod
    def hue(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, _hue)

    @staticmethod
    def saturation(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, _saturation)

    @staticmethod
    def color(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, _color)

    @staticmethod
    def luminosity(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, _luminosity)

    @staticmethod
    def difference(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="abs(a - b)")

    @staticmethod
    def screen(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="a + b - (a * b / 255)")

    @staticmethod
    def linear_dodge(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="a + b")

    @staticmethod
    def subtract(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="a - b")

    @staticmethod
    def multiply(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="a * b / 255")

    @staticmethod
    def lighten(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="max(a, b)")

    @staticmethod
    def darken(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, eval_str="min(a, b)")


def _split_color_and_alpha(img):
    """
    :type img: Image.Image
    :rtype: (tuple(Image.Image), Image.Image)
    """
    if img.mode == "RGBA":
        r, g, b, a = img.split()
        return (r, g, b), a
    elif img.mode == "LA":
        l, a = img.split()
        return (l,), a

    bands = img.split()
    return bands, None


def split_separate_blend(cb, cs):
    """
    :type cb: Image.Image
    :type cs: Image.Image
    :rtype: str, generator[Image.Image, Image.Image], (Image.Image, Image.Image)
    """
    cbc, cba = _split_color_and_alpha(cb)
    csc, csa = _split_color_and_alpha(cs)
    alpha_pair = (cba, csa)

    if cb.mode == cs.mode:
        dst_mode = cb.mode
        color_pair = zip(cbc, csc)
    else:
        dst_mode = cb.mode if len(cbc) >= len(csc) else cs.mode
        if dst_mode in ("RGB", "L"):
            dst_mode += "A" if cba else ""
        last_band = cbc[-1] if len(cbc) < len(csc) else csc[-1]
        color_pair = zip_longest(cbc, csc, fillvalue=last_band)

    return dst_mode, color_pair, alpha_pair


def _put_alpha(cb, img, alpha_pair):
    a = None
    if all(alpha_pair):
        a = ImageMath.eval(
            "a_s + a_b * (255 - a_s)",
            a_b=alpha_pair[0],
            a_s=alpha_pair[1]
        ).convert("L")
    elif alpha_pair[1]:
        a = alpha_pair[1]

    # cs has alpha
    if a:
        base_img = cb.copy()
        base_img.paste(img, mask=a)
        img = base_img

    if alpha_pair[0]:
        img.putalpha(alpha_pair[0])

    return img


def separate_blend(cb, cs, func=None, eval_str="func(float(a), float(b))"):
    """
    :type cb: Image.Image
    :type cs: Image.Image
    :type func: (ImageMath._Operand, ImageMath._Operand) -> ImageMath._Operand | None
    :type eval_str: str
    :rtype: Image.Image
    """
    dst_mode, color_pair, alpha_pair = split_separate_blend(cb, cs)

    bands = []
    if func:
        for a, b in color_pair:
            bands.append(ImageMath.eval(eval_str, func=func, a=a, b=b).convert("L"))
    else:
        for a, b in color_pair:
            bands.append(ImageMath.eval(eval_str, a=a, b=b).convert("L"))

    color_mode = dst_mode if dst_mode not in ("RGBA", "LA") else dst_mode[:-1]
    img = Image.merge(color_mode, bands)

    return _put_alpha(cb, img, alpha_pair)


def no_separate_blend(cb, cs, func):
    """
    :type cb: Image.Image
    :type cs: Image.Image
    :type func: (tuple(ImageMath._Operand), tuple(ImageMath._Operand)) -> Image.Image
    :rtype: Image.Image
    """
    dst_mode, color_pair, alpha_pair = split_separate_blend(cb, cs)

    cb_pack = []
    cs_pack = []
    for bb, bs in color_pair:
        cb_pack.append(ImageMath.eval("float(c)/255", c=bb))
        cs_pack.append(ImageMath.eval("float(c)/255", c=bs))

    r = ImageMath.eval(
        "func((cbr, cbg, cbb), (csr, csg, csb))",
        func=func,
        cbr=cb_pack[0], cbg=cb_pack[1], cbb=cb_pack[2],
        csr=cs_pack[0], csg=cs_pack[1], csb=cs_pack[2],
    )
    img = Image.merge("RGB", [ImageMath.imagemath_convert(c * 255, "L").im for c in r])

    return _put_alpha(cb, img, alpha_pair)


def lum(c):
    """
    :type c: tuple(ImageMath._Operand)
    :rtype: ImageMath._Operand
    """
    return (c[0] * .298912) + (c[1] * 0.586611) + (c[2] * 0.114478)


def sat(c):
    """
    :type c: tuple(ImageMath._Operand)
    :rtype: ImageMath._Operand
    """
    x = ImageMath.imagemath_max(ImageMath.imagemath_max(c[0], c[1]), c[2])
    n = ImageMath.imagemath_min(ImageMath.imagemath_min(c[0], c[1]), c[2])
    return ImageMath.imagemath_float(x - n)


def set_sat(c, s):
    """
    :type c: tuple(ImageMath._Operand)
    :type s: ImageMath._Operand
    :rtype: tuple(ImageMath._Operand)
    """
    x = ImageMath.imagemath_max(ImageMath.imagemath_max(c[0], c[1]), c[2])
    n = ImageMath.imagemath_min(ImageMath.imagemath_min(c[0], c[1]), c[2])
    cs = x - n
    not_even_area = ImageMath.imagemath_int(x != n)

    result = []
    for cc in c:
        max_area = ImageMath.imagemath_int(x == cc)
        min_area = ImageMath.imagemath_int(n == cc)
        mid_area = (max_area ^ 1) & (min_area ^ 1)

        mid = (((cc - n) * s) / cs) * mid_area
        cc = ((s * max_area) + mid) * not_even_area
        result.append(cc)

    return tuple(result)


def clip_color(c):
    """
    :type c: tuple(ImageMath._Operand)
    :rtype: tuple(ImageMath._Operand)
    """
    l = lum(c)
    x = ImageMath.imagemath_max(ImageMath.imagemath_max(c[0], c[1]), c[2])
    n = ImageMath.imagemath_min(ImageMath.imagemath_min(c[0], c[1]), c[2])

    n_l_0 = ImageMath.imagemath_int(n < 0)
    x_b_1 = ImageMath.imagemath_int(x > 1.0)
    l_m_n = l - n
    x_m_l = x - l
    m_l = (1.0 - l)

    if bool(n_l_0):
        c = [
            (_c * (n_l_0 ^ 1)) + ((l + ((_c - l) * l / l_m_n)) * n_l_0)
            for _c in c
            ]

    if bool(x_b_1):
        c = [
            (_c * (x_b_1 ^ 1)) + ((l + ((_c - l) * m_l / x_m_l)) * x_b_1)
            for _c in c
            ]

    return c


def set_lum(c, l):
    """
    :type c: tuple(ImageMath._Operand)
    :type l: ImageMath._Operand
    :rtype: tuple(ImageMath._Operand)
    """
    d = l - lum(c)
    return clip_color((c[0] + d, c[1] + d, c[2] + d))


def _overlay(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    return _hard_light(b, a)


def _soft_light(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    _cl = (a / 255) ** ((255 - b) / 128) * 255
    _ch = (a / 255) ** (128 / b) * 255
    return _cl * (b < 128) + _ch * (b >= 128)


def _hard_light(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    _cl = 2 * a * b / 255
    _ch = 2.0 * (a + b - a * b / 255.0) - 255.0
    return _cl * (b < 128) + _ch * (b >= 128)


def _linear_light(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    _cl = a + (2.0 * b) - 255.0
    _ch = a + (2.0 * (b - 128.0))
    return _cl * (b < 128) + _ch * (b >= 128)


def _exclusion(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    return a + b - ((2.0 * a * b) / 255.0)


def _color_burn(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    non_zero_area = (b != 0)
    fa = a / 255.0
    fb = b / 255.0
    return (1.0 - ((1.0 - fa) / fb)) * 255.0 * non_zero_area


def _color_dodge(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    zero_area = (b == 255)
    dodge = (a / (255 - b)) * 255.0
    return dodge + (zero_area * 255)


# noinspection PyTypeChecker
def _vivid_light(a, b):
    """
    :type a: ImageMath._Operand
    :type b: ImageMath._Operand
    :rtype: ImageMath._Operand
    """
    color_burn = _color_burn(a, b * 2)
    color_dodge = _color_dodge(a, 2 * (b - 128))
    return color_burn * (b < 128) + color_dodge * (b >= 128)


def _hue(cb, cs):
    """
    :type cb: (ImageMath._Operand)
    :type cs: (ImageMath._Operand)
    :rtype: (ImageMath._Operand)
    """
    return set_lum(set_sat(cs, sat(cb)), lum(cb))


def _saturation(cb, cs):
    """
    :type cb: (ImageMath._Operand)
    :type cs: (ImageMath._Operand)
    :rtype: (ImageMath._Operand)
    """
    return set_lum(set_sat(cb, sat(cs)), lum(cb))


def _color(cb, cs):
    """
    :type cb: (ImageMath._Operand)
    :type cs: (ImageMath._Operand)
    :rtype: (ImageMath._Operand)
    """
    return set_lum(cs, lum(cb))


def _luminosity(cb, cs):
    """
    :type cb: (ImageMath._Operand)
    :type cs: (ImageMath._Operand)
    :rtype: (ImageMath._Operand)
    """
    return set_lum(cb, lum(cs))

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


class Image4Layer(object):
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
            None,
            "min(a, 2 * b) * (b < 128) + max(a, 2 * (b - 128)) * (b >= 128)"
        )

    @staticmethod
    def vivid(cb, cs):
        """
        1 - (1 - base) / (2 * ref)    | if ref < 0.5
        base / (1 - 2 * (ref - 0.5))  | otherwise

        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return separate_blend(cb, cs, _vivid)

    @staticmethod
    def hue(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, hue)

    @staticmethod
    def saturation(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, saturation)

    @staticmethod
    def luminosity(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, luminosity)

    @staticmethod
    def color(cb, cs):
        """
        :rtype: Image.Image
        :type cb: Image.Image
        :type cs: Image.Image
        """
        return no_separate_blend(cb, cs, color)

    @staticmethod
    def difference(cb, cs):
        return separate_blend(cb, cs, None, "abs(a - b)")

    @staticmethod
    def screen(cb, cs):
        return separate_blend(cb, cs, None, "a + b - (a * b / 255)")

    @staticmethod
    def linear_dodge(cb, cs):
        return separate_blend(cb, cs, None, "a + b")

    @staticmethod
    def subtract(cb, cs):
        return separate_blend(cb, cs, None, "a - b")

    @staticmethod
    def multiply(cb, cs):
        return separate_blend(cb, cs, None, "a * b / 255")

    @staticmethod
    def lighten(cb, cs):
        return separate_blend(cb, cs, None, "max(a, b)")

    @staticmethod
    def darken(cb, cs):
        return separate_blend(cb, cs, None, "min(a, b)")


def separate_blend(cb, cs, func, eval_str="func(float(a), float(b))"):
    cs_alpha = cs.split()[-1] if _check_alpha(cs) else None
    cb_alpha = cb.split()[-1] if _check_alpha(cb) else None

    num_bands = len(cb.getbands())

    if num_bands > 1:
        bands = []
        for a, b in _band_pair(cb, cs):
            bands.append(ImageMath.eval(eval_str, func=func, a=a, b=b).convert("L"))

        if len(bands) < num_bands:
            bands += cb.split()[len(bands):]

        img = Image.merge(cb.mode, bands)

        # cs has alpha
        if cs_alpha:
            base_img = cb.copy()
            base_img.paste(img, mask=cs_alpha)
            img = base_img

        if cb_alpha:
            img.putalpha(cb_alpha)

        return img
    else:
        return ImageMath.eval(eval_str, func=func, a=cb, b=cs).convert(cb.mode)


def no_separate_blend(cb, cs, func):
    cs_alpha = cs.split()[-1] if _check_alpha(cs) else None
    cb_alpha = cb.split()[-1] if _check_alpha(cb) else None

    if cs_alpha:
        cs = Image.composite(cs.convert("RGB"), Image.new("RGB", cs.size, (0, 0, 0)), cs_alpha)

    cb_pack = [ImageMath.eval("float(c)/255", c=c) for c in cb.split()]
    cs_pack = [ImageMath.eval("float(c)/255", c=c) for c in cs.split()]

    r = ImageMath.eval(
        "func(cbr, cbg, cbb, csr, csg, csb)",
        func=func,
        cbr=cb_pack[0], cbg=cb_pack[1], cbb=cb_pack[2],
        csr=cs_pack[0], csg=cs_pack[1], csb=cs_pack[2],
    )
    result = Image.merge("RGB", [ImageMath.imagemath_convert(c * 255, "L").im for c in r])

    if cs_alpha:
        r = cb.copy()
        r.paste(result, mask=cs_alpha)
        result = r

    if cb_alpha:
        result.putalpha(cb_alpha)

    return result


def _band_pair(cb, cs):
    bands = []
    for img in (cb, cs):
        if _check_alpha(img):
            bands.append(img.split()[:-1])
        else:
            bands.append(img.split())

    b1_len = len(bands[0])
    b2_len = len(bands[1])
    for i in range(b1_len):
        yield bands[0][i], bands[1][min(b2_len - 1, i)]


def _check_alpha(img):
    return img.mode in ("RGBA", "LA")


def lum(c):
    return (c[0] * .298912) + (c[1] * 0.586611) + (c[2] * 0.114478)


def sat(c):
    x = ImageMath.imagemath_max(ImageMath.imagemath_max(c[0], c[1]), c[2])
    n = ImageMath.imagemath_min(ImageMath.imagemath_min(c[0], c[1]), c[2])
    return ImageMath.imagemath_float(x - n)


def set_sat(c, s):
    x = ImageMath.imagemath_max(ImageMath.imagemath_max(c[0], c[1]), c[2])
    n = ImageMath.imagemath_min(ImageMath.imagemath_min(c[0], c[1]), c[2])
    cs = x - n
    not_even_area = ImageMath.imagemath_int(x != n)

    result = []
    for cc in c:
        max_area = ImageMath.imagemath_int(x == cc)
        min_area = ImageMath.imagemath_int(n == cc)
        inv_max_area = (max_area ^ 1)
        inv_min_area = (min_area ^ 1)

        mid_area = inv_max_area & inv_min_area
        mid = (((cc - n) * s) / cs) * mid_area
        cc = ((s * max_area) + mid) * not_even_area
        result.append(cc)

    return result


def clip_color(c):
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
    d = l - lum(c)
    return clip_color((c[0] + d, c[1] + d, c[2] + d))


def _overlay(a, b):
    return _hard_light(b, a)


def _soft_light(a, b):
    _cl = (a / 255) ** ((255 - b) / 128) * 255
    _ch = (a / 255) ** (128 / b) * 255
    return _cl * (b < 128) + _ch * (b >= 128)


def _hard_light(a, b):
    _cl = 2 * a * b / 255
    _ch = 2.0 * (a + b - a * b / 255.0) - 255.0
    return _cl * (b < 128) + _ch * (b >= 128)


def _linear_light(a, b):
    _cl = a + (2.0 * b) - 255.0
    _ch = a + (2.0 * (b - 128.0))
    return _cl * (b < 128) + _ch * (b >= 128)


def _exclusion(a, b):
    return a + b - ((2.0 * a * b) / 255.0)


def _color_burn(a, b):
    non_zero_area = (b != 0)
    fa = a / 255.0
    fb = b / 255.0
    return (1.0 - ((1.0 - fa) / fb)) * 255.0 * non_zero_area


def _color_dodge(a, b):
    zero_area = (b == 255)
    dodge = (a / (255 - b)) * 255.0
    return dodge + (zero_area * 255)


def _vivid(a, b):
    color_burn = _color_burn(a, b * 2)
    color_dodge = _color_dodge(a, 2 * (b - 128))
    return color_burn * (b < 128) + color_dodge * (b >= 128)


def hue(cbr, cbg, cbb, csr, csg, csb):
    cs = (csr, csg, csb)
    cb = (cbr, cbg, cbb)
    return set_lum(set_sat(cs, sat(cb)), lum(cb))


def saturation(cbr, cbg, cbb, csr, csg, csb):
    cs = (csr, csg, csb)
    cb = (cbr, cbg, cbb)
    return set_lum(set_sat(cb, sat(cs)), lum(cb))


def color(cbr, cbg, cbb, csr, csg, csb):
    cs = (csr, csg, csb)
    cb = (cbr, cbg, cbb)
    return set_lum(cs, lum(cb))


def luminosity(cbr, cbg, cbb, csr, csg, csb):
    cs = (csr, csg, csb)
    cb = (cbr, cbg, cbb)
    return set_lum(cb, lum(cs))

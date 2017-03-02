#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Image4Layer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: Copyright 2007-2017 Toshiyuki Ishii.
    :license: MIT, see LICENSE for details.
"""
# noinspection PyPackageRequirements
from PIL import Image, ImageChops, ImageMath  # noqa


class Image4Layer(object):
    @staticmethod
    def overlay(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._overlay)

    @staticmethod
    def _overlay(a, b):
        return Image4Layer._hard_light(b, a)

    @staticmethod
    def soft_light(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._soft_light)

    @staticmethod
    def _soft_light(a, b):
        _cl = (a / 255) ** ((255 - b) / 128) * 255
        _ch = (a / 255) ** (128 / b) * 255
        return _cl * (b < 128) + _ch * (b >= 128)

    @staticmethod
    def hard_light(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._hard_light)

    @staticmethod
    def _hard_light(a, b):
        _cl = 2 * a * b / 255
        _ch = 2.0 * (a + b - a * b / 255.0) - 255.0
        return _cl * (b < 128) + _ch * (b >= 128)

    @staticmethod
    def linear_light(img1, img2):
        """
        base + 2 * ref - 1      | if ref < 0.5
        base + 2 * (ref - 0.5)  | otherwise

        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._linear_light)

    @staticmethod
    def _linear_light(a, b):
        _cl = a + (2.0 * b) - 255.0
        _ch = a + (2.0 * (b - 128.0))
        return _cl * (b < 128) + _ch * (b >= 128)

    @staticmethod
    def exclusion(img1, img2):
        """
        base + ref - (2 * base * ref)

        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._exclusion)

    @staticmethod
    def _exclusion(a, b):
        return a + b - ((2.0 * a * b) / 255.0)

    @staticmethod
    def color_burn(img1, img2):
        """
        1 - (1 - base) / ref

        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._color_burn)

    @staticmethod
    def _color_burn(a, b):
        non_zero_area = (b != 0)
        fa = a / 255.0
        fb = b / 255.0
        return (1.0 - ((1.0 - fa) / fb)) * 255.0 * non_zero_area

    @staticmethod
    def color_dodge(img1, img2):
        """
        base / (1 - ref)

        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._color_dodge)

    @staticmethod
    def _color_dodge(a, b):
        zero_area = (b == 255)
        dodge = (a / (255 - b)) * 255.0
        return dodge + (zero_area * 255)

    @staticmethod
    def pin_light(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(
            img1, img2,
            None,
            "min(a, 2 * b) * (b < 128) + max(a, 2 * (b - 128)) * (b >= 128)"
        )

    @staticmethod
    def vivid(img1, img2):
        """
        1 - (1 - base) / (2 * ref)    | if ref < 0.5
        base / (1 - 2 * (ref - 0.5))  | otherwise

        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return separate_blend(img1, img2, Image4Layer._vivid)

    @staticmethod
    def _vivid(a, b):
        color_burn = Image4Layer._color_burn(a, b * 2)
        color_dodge = Image4Layer._color_dodge(a, 2 * (b - 128))
        return color_burn * (b < 128) + color_dodge * (b >= 128)

    @staticmethod
    def hue(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return no_separate_blend(img1, img2, hue)

    @staticmethod
    def saturation(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return no_separate_blend(img1, img2, saturation)

    @staticmethod
    def luminosity(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return no_separate_blend(img1, img2, luminosity)

    @staticmethod
    def color(img1, img2):
        """
        :rtype: Image.Image
        :type img1: Image.Image
        :type img2: Image.Image
        """
        return no_separate_blend(img1, img2, color)

    @staticmethod
    def difference(img1, img2):
        return separate_blend(img1, img2, None, "abs(a - b)")

    @staticmethod
    def screen(img1, img2):
        return separate_blend(img1, img2, None, "a + b - (a * b / 255)")

    @staticmethod
    def linear_dodge(img1, img2):
        return separate_blend(img1, img2, None, "a + b")

    @staticmethod
    def subtract(img1, img2):
        return separate_blend(img1, img2, None, "a - b")

    @staticmethod
    def multiply(img1, img2):
        return separate_blend(img1, img2, None, "a * b / 255")

    @staticmethod
    def lighten(img1, img2):
        return separate_blend(img1, img2, None, "max(a, b)")

    @staticmethod
    def darken(img1, img2):
        return separate_blend(img1, img2, None, "min(a, b)")


def separate_blend(img1, img2, func, eval_str="func(float(a), float(b))"):
    num_bands = len(img1.getbands())

    if num_bands > 1:
        bands = []
        for a, b in _band_pair(img1, img2):
            bands.append(ImageMath.eval(eval_str, func=func, a=a, b=b).convert("L"))

        if len(bands) < num_bands:
            bands += img1.split()[len(bands):]

        img = Image.merge(img1.mode, bands)

        # img2 has alpha
        if _check_alpha(img2):
            base_img = img1.copy()
            base_img.paste(img, mask=img2.split()[-1])
            img = base_img

        return img
    else:
        return ImageMath.eval(eval_str, func=func, a=img1, b=img2).convert(img1.mode)


def _band_pair(img1, img2):
    bands = []
    for img in (img1, img2):
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


def no_separate_blend(cb, cs, func):
    if cs.mode in ("RGBA", "LA"):
        alpha = cs.split()[-1]
        cs = Image.composite(cs.convert("RGB"), Image.new("RGB", cs.size, (0, 0, 0)), cs.split()[-1])
    else:
        alpha = None

    cb_pack = [ImageMath.eval("float(c)/255", c=c) for c in cb.split()]
    cs_pack = [ImageMath.eval("float(c)/255", c=c) for c in cs.convert("RGB").split()]

    r = ImageMath.eval(
        "func(cbr, cbg, cbb, csr, csg, csb)",
        func=func,
        cbr=cb_pack[0], cbg=cb_pack[1], cbb=cb_pack[2],
        csr=cs_pack[0], csg=cs_pack[1], csb=cs_pack[2],
    )
    rr = Image.merge("RGB", [ImageMath.imagemath_convert(c * 255, "L").im for c in r])

    if alpha:
        result = cb.copy()
        result.paste(rr, mask=alpha)
    else:
        result = rr
    return result


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

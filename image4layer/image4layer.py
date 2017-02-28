#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Image4Layer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: Copyright 2007-2017 Toshiyuki Ishii.
    :license: MIT, see LICENSE for details.
"""
from PIL import Image, ImageChops, ImageMath


class Image4Layer(object):

    @classmethod
    def over_lay(cls, img1, img2):
        """
        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._over_lay)

    @staticmethod
    def _over_lay(a, b):
        _cl = 2 * a * b / 255
        _ch = 2 * (a + b - a * b / 255) - 255
        return _cl * (a < 128) + _ch * (a >= 128)

    @classmethod
    def soft_light(cls, img1, img2):
        """
        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._soft_light)

    @staticmethod
    def _soft_light(a, b):
        _cl = (a / 255) ** ((255 - b) / 128) * 255
        _ch = (a / 255) ** (128 / b) * 255
        return _cl * (b < 128) + _ch * (b >= 128)

    @classmethod
    def hard_light(cls, img1, img2):
        """
        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._hard_light)

    @staticmethod
    def _hard_light(a, b):
        _cl = 2 * a * b / 255
        _ch = 2.0 * (a + b - a * b / 255.0) - 255.0
        return _cl * (b < 128) + _ch * (b >= 128)

    @classmethod
    def linear_light(cls, img1, img2):
        """
        base + 2 * ref - 1      | if ref < 0.5
        base + 2 * (ref - 0.5)  | otherwise

        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._linear_light)

    @staticmethod
    def _linear_light(a, b):
        _cl = a + (2.0 * b) - 255.0
        _ch = a + (2.0 * (b - 128.0))
        return _cl * (b < 128) + _ch * (b >= 128)

    @classmethod
    def exclusion(cls, img1, img2):
        """
        base + ref - (2 * base * ref)

        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._exclusion)

    @staticmethod
    def _exclusion(a, b):
        return a + b - ((2.0 * a * b) / 255.0)

    @classmethod
    def color_burn(cls, img1, img2):
        """
        1 - (1 - base) / ref

        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._color_burn)

    @staticmethod
    def _color_burn(a, b):
        zero_area = (b == 0)
        fa = a / 255.0
        fb = b / 255.0
        return (1.0 - ((1.0 - fa) / fb)) * 255.0 + (zero_area * 255)

    @classmethod
    def color_dodge(cls, img1, img2):
        """
        base / (1 - ref)

        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._color_dodge)

    @staticmethod
    def _color_dodge(a, b):
        zero_area = (b == 255)
        dodge = (a / (255 - b)) * 255.0
        return dodge + (zero_area * 255)

    @classmethod
    def pin_light(cls, img1, img2):
        """
        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return Image4Layer._do_layer(
            img1, img2,
            None,
            "min(a, 2 * b) * (b < 128) + max(a, 2 * (b - 128)) * (b >= 128)"
        )

    @classmethod
    def vivid(cls, img1, img2):
        """
        1 - (1 - base) / (2 * ref)    | if ref < 0.5
        base / (1 - 2 * (ref - 0.5))  | otherwise

        :rtype: Image
        :type img1: Image
        :type img2: Image
        """

        return cls._do_layer(img1, img2, cls._vivid)

    @staticmethod
    def _vivid(a, b):
        color_burn = Image4Layer._color_burn(a, b * 2)
        color_dodge = Image4Layer._color_dodge(a, 2 * (b - 128))
        return color_burn * (b < 128) + color_dodge * (b >= 128)

    @staticmethod
    def difference(img1, img2):
        return ImageChops.difference(img1, img2)

    @staticmethod
    def screen(img1, img2):
        return ImageChops.screen(img1, img2)

    @staticmethod
    def linear_dodge(img1, img2):
        return ImageChops.add(img1, img2)

    @staticmethod
    def subtract(img1, img2):
        return ImageChops.subtract(img1, img2)

    @staticmethod
    def multiply(img1, img2):
        return ImageChops.multiply(img1, img2)

    @staticmethod
    def lighten(img1, img2):
        return ImageChops.lighter(img1, img2)

    @staticmethod
    def darken(img1, img2):
        return ImageChops.darker(img1, img2)

    @staticmethod
    def _do_layer(img1, img2, func, eval_str="func(float(a), float(b))"):
        num_bands = len(img1.getbands())

        if num_bands > 1:
            bands = []
            for a, b in Image4Layer._band_pair(img1, img2):
                bands.append(ImageMath.eval(eval_str, func=func, a=a, b=b).convert("L"))

            if len(bands) < num_bands:
                bands += img1.split()[len(bands):]

            img = Image.merge(img1.mode, bands)

            # img2 has alpha
            if Image4Layer._check_alpha(img2):
                base_img = img1.copy()
                base_img.paste(img, mask=img.split()[-1])
                img = base_img

            return img
        else:
            return ImageMath.eval(eval_str, func=func, a=img1, b=img2).convert(img1.mode)

    @staticmethod
    def _band_pair(img1, img2):
        bands = []
        for img in (img1, img2):
            if Image4Layer._check_alpha(img):
                bands.append(img.split()[:-1])
            else:
                bands.append(img.split())

        b1_len = len(bands[0])
        b2_len = len(bands[1])
        for i in range(b1_len):
            yield bands[0][i], bands[1][min(b2_len-1, i)]

    @staticmethod
    def _check_alpha(img):
        return img.mode in ("RGBA", "LA")


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

    @classmethod
    def soft_light(cls, img1, img2):
        """
        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._soft_light)

    @classmethod
    def hard_light(cls, img1, img2):
        """
        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._hard_light)

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
        fa = a / 255.0
        fb = b / 255.0
        _cl = (1.0 - ((1.0 - fa) / (2 * fb))) * 255.0
        _ch = (fa / (1.0 - (2.0 * (fb - 0.5)))) * 255.0
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
    def pin_light(cls, img1, img2):
        """
        :rtype: Image
        :type img1: Image
        :type img2: Image
        """
        return cls._do_layer(img1, img2, cls._pin_light)

    @staticmethod
    def _pin_light(a, b):
        _cl = min(a, 2.0 * b)
        _ch = max(a, 2.0 * (b - 128))
        return _cl * (b < 128) + _ch * (b >= 128)

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
    def _do_layer(img1, img2, func):
        eval_str = "func(float(a), float(b))"
        num_bands = len(img1.getbands())

        if num_bands > 1:
            bands = []
            for a, b in zip(img1.split(), img2.split()):
                bands.append(ImageMath.eval(eval_str, func=func, a=a, b=b).convert("L"))

            if len(bands) < num_bands:
                bands += img1.split()[len(bands):]

            img = Image.merge(img1.mode, bands)
            if img2.mode == "RGBA" or img2.mode == "LA":
                base_img = img1.copy()
                base_img.paste(img, mask=img.split()[-1])
                img = base_img

            return img
        else:
            return ImageMath.eval(eval_str, func=func, a=img1, b=img2).convert(img1.mode)

    @staticmethod
    def _band_pair(img1, img2):
        if img1.mode == img2.mode:
            if img1.mode ==
            for x in zip(img1.split(), img2.split()):
                yield x

    @staticmethod
    def _over_lay(a, b):
        _cl = 2 * a * b / 255
        _ch = 2 * (a + b - a * b / 255) - 255
        return _cl * (a < 128) + _ch * (a >= 128)

    @staticmethod
    def _soft_light(a, b):
        _cl = (a / 255) ** ((255 - b) / 128) * 255
        _ch = (a / 255) ** (128 / b) * 255
        return _cl * (b < 128) + _ch * (b >= 128)

    @staticmethod
    def _hard_light(a, b):
        _cl = 2 * a * b / 255
        _ch = 2.0 * (a + b - a * b / 255.0) - 255.0
        return _cl * (b < 128) + _ch * (b >= 128)


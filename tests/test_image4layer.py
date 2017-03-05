#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PIL import Image
from image4layer import Image4Layer
from image4layer.image4layer import split_separate_blend


def test_duck():
    source = Image.open("ducky.png")
    backdrop = Image.open("backdrop.png")

    Image4Layer.multiply(backdrop, source)


def test_layer():
    img1 = Image.open("sample.png")
    img2 = Image.open("effect.png")
    a_img = Image.open("alpha.png")

    Image4Layer.overlay(img1, img2)
    Image4Layer.overlay(img1, a_img)
    Image4Layer.overlay(a_img, img1)

    Image4Layer.soft_light(img1, img2)
    Image4Layer.hard_light(img1, img2)

    Image4Layer.color_burn(img1, img2)
    Image4Layer.color_dodge(img1, img2)
    Image4Layer.vivid(img1, img2)

    Image4Layer.darken(img1, img2)
    Image4Layer.lighten(img1, img2)
    Image4Layer.pin_light(img1, img2)


def test_hue():
    img1 = Image.open("sample.png")
    img2 = Image.open("color.png")

    Image4Layer.hue(img1, img2)
    Image4Layer.saturation(img1, img2)
    Image4Layer.luminosity(img1, img2)
    Image4Layer.color(img1, img2)


def test_alpha_mode():
    rgb = Image.new("RGB", (1, 1), (255, 0, 0))
    rgba = Image.new("RGBA", (1, 1), (255, 0, 0, 128))
    l = Image.new("L", (1, 1), 255)
    la = Image.new("LA", (1, 1), (255, 255))
    hsv = Image.new("HSV", (1, 1), (0, 0, 0))
    cmyk = Image.new("CMYK", (1, 1), (0, 0, 0, 0))

    dst_mode, color_pair, alpha_pair = split_separate_blend(rgb, rgba)
    assert dst_mode == "RGB"

    dst_mode, color_pair, alpha_pair = split_separate_blend(rgba, rgb)
    assert dst_mode == "RGBA"

    dst_mode, color_pair, alpha_pair = split_separate_blend(rgb, l)
    assert dst_mode == "RGB"

    dst_mode, color_pair, alpha_pair = split_separate_blend(l, rgb)
    assert dst_mode == "RGB"

    dst_mode, color_pair, alpha_pair = split_separate_blend(la, rgb)
    assert dst_mode == "RGBA"

    dst_mode, color_pair, alpha_pair = split_separate_blend(l, la)
    assert dst_mode == "L"

    dst_mode, color_pair, alpha_pair = split_separate_blend(la, l)
    assert dst_mode == "LA"

    dst_mode, color_pair, alpha_pair = split_separate_blend(rgb, la)
    assert dst_mode == "RGB"
    colors = [(a.getpixel((0, 0)), b.getpixel((0, 0))) for a, b in color_pair]
    assert colors == [(255, 255), (0, 255), (0, 255)]

    dst_mode, color_pair, alpha_pair = split_separate_blend(hsv, l)
    assert dst_mode == "HSV"

    dst_mode, color_pair, alpha_pair = split_separate_blend(cmyk, l)
    assert dst_mode == "CMYK"
    # assert False


def test_mode_pair():
    img1 = Image.open("sample.png")
    img2 = Image.open("effect.png")
    a_img = Image.open("alpha.png")

    # L &  L
    Image4Layer.overlay(img1.convert("L"), img2.convert("L"))
    # RGB & L
    Image4Layer.overlay(img1, img2.convert("L"))
    # RGBA & L
    img = Image4Layer.overlay(a_img, img2.convert("L"))
    assert img.mode == "RGBA"
    # HSV & L
    Image4Layer.overlay(img1.convert("HSV"), img2.convert("L"))
    # CMYK & L
    Image4Layer.overlay(img1.convert("CMYK"), img2.convert("L"))

    # L & RGB
    img = Image4Layer.overlay(img2.convert("L"), img1.convert("RGB"))
    assert img.mode == "L"

    # RGBA & L
    img = Image4Layer.hue(a_img, img2)
    assert img.mode == "RGBA"

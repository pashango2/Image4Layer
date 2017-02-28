#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PIL import Image
from image4layer import Image4Layer


def test_layer():
    img1 = Image.open("sample.png")
    img2 = Image.open("effect.png")
    a_img = Image.open("alpha.png")

    Image4Layer.over_lay(img1, img2)
    Image4Layer.soft_light(img1, img2)
    Image4Layer.hard_light(img1, img2)

    Image4Layer.over_lay(img1, a_img)
    Image4Layer.over_lay(a_img, img1)

    Image4Layer.color_burn(img1, img2)
    Image4Layer.color_dodge(img1, img2)
    Image4Layer.vivid(img1, img2)

    Image4Layer.darken(img1, img2)
    Image4Layer.lighten(img1, img2)
    Image4Layer.pin_light(img1, img2)


def test_mode_pair():
    img1 = Image.open("sample.png")
    img2 = Image.open("effect.png")
    a_img = Image.open("alpha.png")

    # L &  L
    Image4Layer.over_lay(img1.convert("L"), img2.convert("L"))
    # RGB & L
    Image4Layer.over_lay(img1, img2.convert("L"))
    # RGBA & L
    img = Image4Layer.over_lay(a_img, img2.convert("L"))
    assert img.mode == "RGBA"
    # HSV & L
    Image4Layer.over_lay(img1.convert("HSV"), img2.convert("L"))
    # CMYK & L
    Image4Layer.over_lay(img1.convert("CMYK"), img2.convert("L"))

    # L & RGB
    img = Image4Layer.over_lay(img2.convert("L"), img1.convert("RGB"))
    assert img.mode == "L"







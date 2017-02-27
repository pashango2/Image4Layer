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

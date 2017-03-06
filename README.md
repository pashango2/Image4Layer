
#  Image4Layer

It is implemented by 'pillow' in blend mode of CSS3. And more...

# Install

```
pip install image4layer
```

# Usage


```python
from PIL import Image
from image4layer import Image4Layer

source = Image.open("tests/ducky.png")
backdrop = Image.open("tests/backdrop.png")
```


```python
Image4Layer.__version__
```




    '0.43'



# Separable blend modes

### normal


```python
Image4Layer.normal(backdrop, source)
```


![png](imgs/output_5_0.png)


### multiply


```python
Image4Layer.multiply(backdrop, source)
```


![png](imgs/output_7_0.png)


### screen


```python
Image4Layer.screen(backdrop, source)
```


![png](imgs/output_9_0.png)


### overlay


```python
Image4Layer.overlay(backdrop, source)
```


![png](imgs/output_11_0.png)


### darken


```python
Image4Layer.darken(backdrop, source)
```


![png](imgs/output_13_0.png)


### lighten


```python
Image4Layer.lighten(backdrop, source)
```


![png](imgs/output_15_0.png)


### color-dodge


```python
Image4Layer.color_dodge(backdrop, source)
```


![png](imgs/output_17_0.png)


### color-burn


```python
Image4Layer.color_burn(backdrop, source)
```


![png](imgs/output_19_0.png)


### hard-light


```python
Image4Layer.hard_light(backdrop, source)
```


![png](imgs/output_21_0.png)


### soft-light


```python
Image4Layer.soft_light(backdrop, source)
```


![png](imgs/output_23_0.png)


### difference


```python
Image4Layer.difference(backdrop, source)
```


![png](imgs/output_25_0.png)


### exclusion


```python
Image4Layer.exclusion(backdrop, source)
```


![png](imgs/output_27_0.png)


# Non-separable blend modes

### hue


```python
Image4Layer.hue(backdrop, source)
```


![png](imgs/output_30_0.png)


### saturation


```python
Image4Layer.saturation(backdrop, source)
```


![png](imgs/output_32_0.png)


### color


```python
Image4Layer.color(backdrop, source)
```


![png](imgs/output_34_0.png)


### luminosity


```python
Image4Layer.luminosity(backdrop, source)
```


![png](imgs/output_36_0.png)


# More blend modes

### vivid-light


```python
Image4Layer.vivid_light(backdrop, source)
```


![png](imgs/output_39_0.png)


### pin-light


```python
Image4Layer.pin_light(backdrop, source)
```


![png](imgs/output_41_0.png)


### linear-dodge


```python
Image4Layer.linear_dodge(backdrop, source)
```


![png](imgs/output_43_0.png)


### subtract


```python
Image4Layer.subtract(backdrop, source)
```


![png](imgs/output_45_0.png)


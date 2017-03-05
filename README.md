# Image4Layer

It is implemented by 'pillow' in blend mode of CSS3.


## Install

```
pip install image4layer
```

## Usage

```python
from PIL import Image
from image4layer import Image4Layer

source = Image.open("ducky.png")
backdrop = Image.open("backdrop.png")

Image4Layer.multiply(backdrop, source)
```


from distutils.core import setup
from image4layer import __version__

setup(
    name='Image4Layer',
    version=__version__,
    packages=['image4layer'],
    package_dir={'image4layer': 'image4layer'},
    url='https://github.com/pashango2/Image4Layer',
    license='MIT',
    author='Toshiyuki Ishii',
    author_email='pashango2@gmail.com',
    description='layer effects by pillow'
)

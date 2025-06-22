from distutils.core import setup
from Cython.Build import cythonize
 
setup(
    name="baba",
    ext_modules = cythonize(["./*.py"], language_level=3)
)
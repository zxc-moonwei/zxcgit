from setuptools import setup
# 4/28
setup(name="zxcgit",
      packages=['zxcgit'],
      entry_points=
      {'console_scripts': ['zxcgit = zxcgit.cli:main']}
      )

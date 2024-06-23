from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='cae_model',
  version='0.0.1',
  author='Artem Antonov',
  author_email='artmihant@gmail.com',
  description='Read & Write parser for FC (fidesys calc) and VTU (VTK unstructed grid) file types',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/artmihant/CAEmodel',
  packages=find_packages(),
  classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers"
  ],
  keywords='example python',
  python_requires='>=3.7'
)

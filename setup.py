from setuptools import setup

setup(name='busypal',
      version='1.0.0',
      description='Shows a busy indicator for long-running operations while it is still processing',
      url='https://github.com/cosmicshear/busypal',
      author='Erfan Nourbakhsh',
      author_email='erfanxyz@gmail.com',
      license='MIT',
      packages=['busypal'],
      install_requires=[
          "psutil",
          "colored",
      ],
      zip_safe=False)

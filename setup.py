"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')


install_requires = [
    "bottle>=0.12.8,<=0.13",
    "boxsdk>=2.0,<3.0",
    "pyinotify==0.9.6",
    "redis~=3.3.0",
    "requests>=2.20.0,<3.0",
    "pyopenssl>=16.0.0",
    "cherrypy>=13.0.0",
]

extras_require = {
    "dev": ["ipython>=7.0", "check-manifest", ],
    "test": ["tox", ],
}

setup(
    name="diycrate",
    version="0.2.11.0rc6",
    author="Jason Held",
    author_email="jasonsheld@gmail.com",
    description="box.com for linux -- unofficial, based on python SDK",
    keywords="cloud storage box.com sdk linux box",
    url="https://github.com/jheld/diycrate",
    install_requires=install_requires,
    test_suite="tests",
    extras_require=extras_require,
    packages=find_packages(exclude=['tests', 'tests.*']),
    entry_points={
      'console_scripts': [
        'diycrate_app=diycrate.diycrate_app:main',
        'diycrate_server=diycrate.server_app:main',
      ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    python_requires='>=3.5,<4',
    project_urls={
        'Source': 'https://github.com/jheld/diycrate/',
        'Issues': 'https://github.com/jheld/diycrate/issues',
    },
)

import re
import setuptools


# Grab the readme
try:
    with open("README.md", "r") as a:
        long_description = a.read()
except Exception:
    long_description = ""


# Here are the requirements
requirements = [
    "novus>=0.0.1,<0.1",
    "toml>=0.10.2,<0.11",
    "asyncpg>=0.21.0,<0.22",
    "aioredis>=1.3,<2.0",
    "aioredlock>=0.7.0,<0.8",
    "aiodogstatsd>=0.14.0,<0.15",
    "aiohttp",  # no versioning here because I trust u
    "upgradechatpy>=1.0.3<2.0"
]


# Here are some MORE requirements
extras = {
    "web": [
        "cryptography>=3.3.1,<4.0",
        "aiohttp_jinja2>=1.4.2,<2.0",
        "aiohttp_session>=2.9.0,<3.0",
        "jinja2>=2.11.2,<3.0",
        "markdown>=3.3.3,<4.0",
        "htmlmin>=0.1.12,<0.2",
    ],
    "docs": [
        "sphinx",
        "sphinx_rtd_theme",
    ]
}


# Let's get the version
version = None
regex = re.compile(r"""["']((?:[\d.]+)(?:a|b)?)["']""", re.MULTILINE)
with open("voxelbotutils/__init__.py") as a:
    text = a.read()
version = regex.search(text).group(1)


setuptools.setup(
    name="voxelbotutils",
    version=version,
    author="Kae Bartlett",
    author_email="kae@voxelfox.co.uk",
    description="A set of bot utilities for Novus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Voxel-Fox-Ltd/VoxelBotUtils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require=extras,
    entry_points={
        "console_scripts": [
            "voxelbotutils=voxelbotutils.__main__:main",
            "vbu=voxelbotutils.__main__:main",
        ],
    },
)

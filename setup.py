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
    "discord.py>=1.6,<2.0",
    "toml",
    "asyncpg",
    "aioredis",
    "aioredlock",
    "aiodogstatsd",
    "aiohttp",
]


# Here are some MORE requirements
extras = {
    "web": [
        "cryptography",
        "aiohttp_jinja2",
        "aiohttp_session",
        "jinja2",
        "markdown",
        "htmlmin",
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
    description="A set of bot utilities for Discord.py",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Voxel-Fox-Ltd/VoxelBotUtils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    extras_require=extras,
    entry_points={
        "console_scripts": [
            "voxelbotutils=voxelbotutils.__main__:main",
            "vbu=voxelbotutils.__main__:main",
        ],
    },
)

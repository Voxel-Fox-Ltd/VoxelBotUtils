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
    "discord.py>=1.5.0",
    "toml",
    "asyncpg",
    "aioredis",
    "aiodogstatsd",
]


# Let's get the version
version = None
regex = re.compile(r"""["']((?:[\d.]+)(?:a|b)?)["']""", re.MULTILINE)
with open("voxelbotutils/__init__.py") as a:
    text = a.read()
version = regex.search(text).group(1)


setuptools.setup(
    name="voxelbotutils",
    version=version,
    author="Caleb Bartlett",
    author_email="callum@voxelfox.co.uk",
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
)

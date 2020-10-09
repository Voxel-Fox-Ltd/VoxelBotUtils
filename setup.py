import setuptools
from voxelbotutils import __version__

try:
    with open("README.md", "r") as a:
        long_description = a.read()
except Exception:
    long_description = ""

requirements = []
try:
    with open("requirements.txt", "r") as a:
        requirements_string = a.read()
    for line in requirements_string.strip().split('\n'):
        if line.startswith('#') or not line.strip():
            pass
        else:
            requirements.append(line.strip())
except Exception:
    pass

setuptools.setup(
    name="voxelbotutils",
    version=__version__,
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

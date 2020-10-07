import setuptools

try:
    with open("README.md", "r") as a:
        long_description = a.read()
except Exception:
    long_description = ""

setuptools.setup(
    name="voxelbotutils",
    version="0.0.3",
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
)

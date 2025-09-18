"""
Setup script for the Talki package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="talki",
    version="1.0.0",
    author="Talki Team",
    description="Real-Time Speech-to-Text Transcription Application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.0.0",
        "faster-whisper>=0.9.0",
        "sounddevice>=0.4.0",
        "numpy>=1.20.0",
        "pynput>=1.7.0",
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "talki=talki.main:main",
        ],
    },
)

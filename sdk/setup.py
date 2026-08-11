"""Packaging configuration for the MD2HTML Python SDK."""

from pathlib import Path

from setuptools import setup

ROOT = Path(__file__).resolve().parent
README = ROOT / "README_SDK.md"

setup(
    name="md2html-client",
    version="0.1.0",
    description="Small Python client for the MD2HTML API",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    py_modules=["md2html_client"],
    python_requires=">=3.8",
    install_requires=[],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
    ],
)

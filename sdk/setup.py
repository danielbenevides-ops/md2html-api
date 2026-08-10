#!/usr/bin/env python3
"""
setup.py — pip-installable package for the MD2HTML Python SDK.

Install (user-local, no virtualenv needed)::

    cd autonomous-business-product/sdk
    pip install .

Then use::

    from md2html_client import MD2HTMLClient
    client = MD2HTMLClient()
    print(client.convert("# Hello"))

The package ships a single module — md2html_client — and has **zero**
external dependencies (only Python 3.8+ standard library).
"""

import os
from setuptools import setup

# Long description: use the module's own docstring so PyPI / index shows it.
long_description = """\
md2html-client — Python SDK for the MD2HTML API
===============================================

A clean, dependency-free Python 3.8+ client for the MD2HTML Markdown-to-HTML
conversion service.

* **Zero dependencies** — uses only the Python standard library (urllib).
* **Thread-safe async** — every method has a non-blocking _async variant.
* **Professional** — typed signatures, custom exception class, payment-hint
  handling, automatic API-key storage on register().

Live API: http://147.15.103.217/md2html/

Quick start
-----------

::

    pip install md2html-client

    python -c "from md2html_client import MD2HTMLClient; c=MD2HTMLClient(); print(c.health())"

Endpoints covered
-----------------

* health()      — GET  /health
* register()     — GET  /register
* convert(md)    — POST /convert
* payment()      — GET  /payment
* usage()        — GET  /usage
* stats()        — GET  /stats
* prettify_json(j) — POST /json/prettify
* text_stats(t)    — POST /text/stats
* slug(s)          — POST /slug
* docs()           — GET  /docs

License: MIT
"""

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="md2html-client",
    version="1.0.0",
    description="Python SDK for the MD2HTML Markdown-to-HTML conversion API (stdlib only).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MD2HTML API project",
    author_email="dcn13l@users.noreply.github.com",
    url="https://github.com/dcn13l/md2html-api",
    license="MIT",
    # Single-file module shipping
    py_modules=["md2html_client"],
    # Allow the importable name to match the class-less lowercase form too.
    packages=[],
    install_requires=[],            # zero external deps
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    # `python -m md2html_client` should print the usage example.
    entry_points={
        "console_scripts": [
            "md2html-client=md2html_client:_example",
        ],
    },
)

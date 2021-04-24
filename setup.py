# coding:utf-8

from setuptools import setup

setup(
    name="knitkit",
    url='https://github.com/colin4124',
    packages=["knitkit"],
    package_data={
        "knitkit": [
            "jars/knitkit.jar",
            "assets/default.yaml",
            "assets/build.sc",
            "assets/project.mk",
            "assets/Main.scala",
        ],
    },
    use_scm_version={"relative_to": __file__, "write_to": "knitkit/version.py",},
    author="Leway Colin",
    author_email="colinlin@gmail.com",
    description=(
        "Knit Kit is a framework that can help to build project easier."
    ),
    license="Apache-2.0 License",
    keywords=[
        "verilog",
        "chisel",
        "rtl",
    ],
    entry_points={"console_scripts": ["knitkit = knitkit.main:main"]},
    setup_requires=["setuptools_scm",],
    install_requires=[
        "mill-bin",
        "mill-cache",
        "pyyaml",
    ],
    # Supported Python versions: 3.6+
    python_requires=">=3.6",
)

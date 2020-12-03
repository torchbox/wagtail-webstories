from setuptools import setup

setup(
    name="wagtail-webstories",
    version="0.0.1",
    packages=["wagtail_webstories"],
    test_suite="tests",

    author="Matt Westcott",
    author_email="matthew@torchbox.com",
    description="AMP web story support for Wagtail",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "webstories>=0.0.1,<0.1",
        "requests>=2.24.0,<3",
        "beautifulsoup4>=4.6,<5",
    ],
    extras_require={
        "testing": [
            "responses>=0.12,<1",
            "Pillow>=4.0.0,<9.0.0",
        ]
    },
    license="BSD",
)

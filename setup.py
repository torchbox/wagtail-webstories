from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wagtail-webstories",
    version="0.0.3",
    packages=["wagtail_webstories"],
    include_package_data=True,
    test_suite="tests",
    url="https://github.com/torchbox/wagtail-webstories/",

    author="Matt Westcott",
    author_email="matthew@torchbox.com",
    description="AMP web story support for Wagtail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Framework :: Wagtail :: 2",
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
            "wagtailmedia>=0.6,<0.8",
        ]
    },
    license="BSD",
)

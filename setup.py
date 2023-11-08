from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wagtail-webstories",
    version="0.1",
    packages=find_packages(exclude=('tests', 'tests.*')),
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
        "Framework :: Django",
        "Framework :: Django :: 3",
        "Framework :: Django :: 4",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 4",
        "Framework :: Wagtail :: 5",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "wagtail>=4.1",
        "webstories>=0.0.1,<1",
        "requests>=2.24.0,<3",
        "beautifulsoup4>=4.6,<5",
    ],
    extras_require={
        "testing": [
            "tox",
            "responses>=0.12,<1",
            "Pillow>=4.0.0,<10.0.0",
            "wagtailmedia>=0.6,<0.15",
        ]
    },
    license="BSD",
)

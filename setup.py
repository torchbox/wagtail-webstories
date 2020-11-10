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
        "webstoryparser @ git+ssh://git@github.com/gasman/webstoryparser@master#egg=webstoryparser",
    ],
    license="BSD",
)

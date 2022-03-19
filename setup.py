from setuptools import setup, find_packages
from scoretweets import __version__


def read_file(filename, lines=False):
    try:
        with open(filename, "r") as f:
            if lines:
                return [i.strip() for i in f.read().split('\n') if i.strip()]
            return f.read()
    except:
        print("Can not read file:", filename)
        return None

long_description = read_file("README.md")

setup(
    name="scoretweets",
    version=__version__,
    author="Ibrahim Rafi",
    author_email="me@ibrahimrafi.me",
    license="MIT",
    url="https://github.com/rafiibrahim8/ScoreTweets",
    download_url="https://github.com/rafiibrahim8/ScoreTweets/archive/v{}.tar.gz".format(
        __version__
    ),
    install_requires=read_file('requirements.txt', True),
    description="Automatically post PCSPro score tweets to facebook and discord.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["scoretweets", "PCSPro", "Cricket Scores"],
    packages=find_packages(),
    entry_points=dict(console_scripts=["scoretweets=scoretweets.scoretweets:main"]),
    platforms=["any"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

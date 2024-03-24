import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
        name="mangue",
        version="0.2.0",
        author="Egsagon",
        description="A Python Downloader of mangas.io",
        license="GPLv3",
        url="https://github.com/Egsagon/mangue",
        install_requires=[
            "tqdm",
            "requests",
            "pwinput",
        ],
        long_description=long_description,
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GPLv3 License",
            "Operating System :: OS Independent",
        ],
        packages=setuptools.find_packages(),
        python_requires=">=3.9",
)

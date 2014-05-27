import setuptools

setuptools.setup(
    name = "EAST",
    packages = setuptools.find_packages(),
    version = "0.1",
    description = "Text analysis library based on the Annotated Suffix Tree method",

    install_requires = [
        "numpy>=1.7.1",
        "docutils>=0.3",
        "testtools>=0.9.35"
    ],

    author = "Mikhail Dubov",
    author_email = "msdubov@gmail.com",
    license = "MIT",
    url = "https://github.com/msdubov/AST-text-analysis",
    download_url = "https://github.com/msdubov/AST-text-analysis/tarball/0.1",
    keywords = ["text analysis", "suffix tree", "synonym extraction"]
)

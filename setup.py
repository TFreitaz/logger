import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logger",
    version="0.0.1",
    author="TFreitaz",
    author_email="thales.zfreitas@gmail.com",
    description="Easy creation and upload of full detailed logs.",
    long_description=long_description,
    url="https://github.com/arocketman/git-and-pip",
    packages=setuptools.find_packages(),
    install_requires=["cryptography==3.2.1", "elasticsearch==6.8.1", "python-dotenv==0.15.0"],
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent"],
)

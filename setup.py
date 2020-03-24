from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="limit-handling-demo",
    version="0.1.0",
    description="Limit handling demo",
    author="Balazs Gibizer",
    author_email="gibizer@gmail.com",
    url="https://github.com/gibizer/limit-handling-demo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    packages=["limit_handling"],
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[],
)

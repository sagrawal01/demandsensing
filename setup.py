import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="demandsensing",
    version="0.0.1",
    author="Shubhangi Agrawal", #Add additional names here
    author_email="sagrawal213@gmail.com",
    description="Time series analysis to predict demand based on historical demand and commercial data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sagrawal01/demandsensing",
    install_requires=['pandas', 'SQLAlchemy', 'datetime', 'xgboost', 'python-dateutil', 'numpy', 'cryptography', 'psycopg2', 'openpyxl'],
    project_urls={
        "Bug Tracker": "https://github.com/sagrawal01/demandsensing/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent (built on macOS Mojave Version 10.14.6)",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

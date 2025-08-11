from setuptools import setup, find_packages

setup(
    name="nonix_mini_artist",
    version="0.1.0",
    description="Simple music metadata management system",
    author="Nonix",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "peewee>=3.16.0",
        "nicegui>=1.4.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "aiofiles>=23.0.0",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)

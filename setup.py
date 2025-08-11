from setuptools import setup, find_packages

setup(
    name="nonix_mini_artist",
    version="0.2.0",
    description="Simple music metadata management system with Google AI integration",
    author="Nonix",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "peewee>=3.16.0",
        "nicegui>=1.4.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "pyyaml>=6.0",
        "aiofiles>=23.0.0",
        "google-generativeai>=0.3.0",
        "google-cloud-aiplatform>=1.38.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)

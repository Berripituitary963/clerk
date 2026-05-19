from setuptools import setup, find_packages

setup(
    name="clerk-api",
    version="0.1.0",
    description="Python SDK for Clerk — US federal court records API",
    author="Solvr",
    url="https://clerk.solvrlabs.ai",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["httpx>=0.24.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

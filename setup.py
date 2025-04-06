from setuptools import setup, find_packages

setup(
    name="toast-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "win10toast;platform_system=='Windows'",
    ],
    python_requires=">=3.8",
)

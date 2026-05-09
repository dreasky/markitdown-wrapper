from setuptools import setup, find_packages

setup(
    name="markitdown-wrapper",
    version="0.1.2",
    packages=find_packages(include=["markitdown_wrapper*"]),
    package_data={"markitdown_wrapper": ["markitdown_config.json"]},
    install_requires=[
        "markitdown[all]>=0.1.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "markitdown-ocr",
        "chardet",
        "markdownify",
    ],
    python_requires=">=3.10",
)

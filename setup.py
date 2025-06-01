from setuptools import setup, find_packages

setup(
    name="git-commit-summarizer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gitpython>=3.1.30",
        "click>=8.1.3",
        "colorama>=0.4.6",
        "tqdm>=4.65.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "local_ai": [
            "transformers>=4.28.0",
            "torch>=2.0.0",
        ],
        "dev": [
            "pytest>=7.3.1",
            "black>=23.3.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "git-commit-summarizer=src.cli:main",
        ],
    },
    author="meliem",
    author_email="meliem@example.com",
    description="A tool that automatically generates commit messages from code changes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/meliem/ai-commit-summarizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)

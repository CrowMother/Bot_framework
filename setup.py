from setuptools import setup, find_packages

setup(
    name="trading_bot_lib",  # Name of your library
    version="0.1.0",  # Initial version
    author="Your Name",
    author_email="your.email@example.com",
    description="A framework for creating trading bots with Schwab integration.",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",  # README is in Markdown format
    url="https://github.com/yourusername/trading_bot_lib",  # Replace with your repo URL
    packages=find_packages(where="App"),  # Find packages inside the "App" directory
    package_dir={"": "App"},  # Define the root directory for packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Minimum Python version requirement
    install_requires=[  # Add dependencies your library needs
        "numpy",  # Example: Replace or extend with actual dependencies
    ],
    extras_require={  # Optional dependencies for development
        "dev": [
            "pytest",  # Testing framework
            "flake8",  # Linting tool
        ],
    },
)

from setuptools import setup, find_packages

setup(
    name="Bot_App",                       # Library name
    version="0.1.0",                      # Version
    author="Asa",
    author_email="your.email@example.com",
    description="Simplified library for creating account tracking bots",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CrowMother/Bot_framework",  # Replace with your repository URL
    packages=find_packages(where="src"),  # Finds packages in 'src'
    package_dir={"": "src"},              # 'src' is the root directory for packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
     install_requires=[
         "pandas",
         "logging",
         "schwabdev",
         "typing",
        "python-dotenv"
    ],  # Add runtime dependencies if any
    extras_require={
        "dev": ["pytest", "flake8"],  # Add development dependencies
    },
)

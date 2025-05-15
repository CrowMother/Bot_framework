from setuptools import setup, find_packages

setup(
    name="Bot_App",
    version="0.3.0",
    packages=find_packages(include=["Bot_App", "Bot_App.*"]),
    include_package_data=True,
    install_requires=[
        "requests", "pandas", "python-dotenv", "schwabdev"
    ]
)

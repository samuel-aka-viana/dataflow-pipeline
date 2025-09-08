from setuptools import setup, find_packages

setup(
    name='dataflow-pipeline',
    version='0.1.0',
    description='Apache Beam pipeline for data processing',
    packages=find_packages(),
    install_requires=[
        "apache-beam[gcp]>=2.67.0",
        "faker>=37.6.0",
        "pandas>=2.3.2",
        "python-dotenv>=1.1.1"
    ],
    python_requires='>=3.12',
    include_package_data=True,
)

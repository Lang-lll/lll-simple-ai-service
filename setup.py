from setuptools import setup, find_packages

setup(
    name="lll-simple-ai-service",
    version="0.1.0",
    description="Structured AI service with Outlines for JSON output",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "outlines>=0.0.25",
        "flask>=2.0.0",
        "requests>=2.25.0",
        "pyyaml>=6.0",
        "huggingface-hub>=0.16.0",
    ],
    setup_requires=[
        "setuptools>=45.0",
        "wheel",
        "setuptools_scm",
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "ai-service=scripts.start_service:main",
            "ai-service-download=scripts.download_model:main",
        ],
    },
)

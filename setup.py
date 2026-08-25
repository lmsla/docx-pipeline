from setuptools import find_packages, setup

setup(
    name="docx-pipeline",
    version="0.2.3",
    description="Markdown to enterprise DOCX pipeline with reference template and post-processing.",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=["python-docx>=1.1.2"],
    entry_points={
        "console_scripts": [
            "docx-pipeline=docx_pipeline.cli:main",
        ],
    },
)

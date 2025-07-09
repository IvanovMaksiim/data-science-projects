from setuptools import setup, find_packages

setup(
    name="adaptive_knn_kdtree",
    version="0.1",
    packages=find_packages(),
    install_requires=["numpy"],
    author="Your Name",
    description="Adaptive KNN classifier using KD-Tree",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

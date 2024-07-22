import setuptools

VERSION = "1.1.2"
PACKAGE_NAME = "meteohub"

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=["Valerio Luzzi", "Marco Renzi", "Stefano Bagli"],
    author_email="valerio.luzzi@gecosistema.com",
    description="Template for command-line python program",
    long_description="Template for command-line python program",
    url=f"https://github.com/SaferPlaces2023/{PACKAGE_NAME}.git",
    packages=setuptools.find_packages(where="src"),
    package_dir={"":"src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'wheel',
        'setuptools',
        'click',
        'ecmwflibs',
        'requests',
        'pandas',
        'rasterio',
        'xarray[complete]',
        'pygrib',
        'cfgrib',
        'numpy',
    ],
    entry_points="""
      [console_scripts]
      meteohub=meteohub.main:main
      """,
)
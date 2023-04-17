# `geolab `: geotechnical engineering software for students and professionals.

[![](https://img.shields.io/badge/PyPi-Pato546-blue?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/user/Pato546/)
![](https://img.shields.io/pypi/l/geolab?style=flat-square)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![](https://img.shields.io/badge/code%20formatter-docformatter-fedcba.svg?style=flat-square)](https://github.com/PyCQA/docformatter)
[![](https://img.shields.io/badge/%20style-google-3666d6.svg?style=flat-square)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings)
![](https://img.shields.io/github/repo-size/patrickboateng/geolab?style=flat-square&labelColor=ef8336)
![](https://img.shields.io/pypi/dm/geolab?style=flat-square)

`geolab` implements various geotechnical methods such as soil classification (USCS, AASHTO). Also, `geolab` implements methods for estimating soil engineering properties such as bearing capacity ($q_{ult}$), void ratio ($e_o$), undrained shear strength($C_u$), internal angle of friction ($\phi$) etc.

> **&#9432;** Only Unified Soil Classification (USCS) has been implemented as of now and can also be installed as a Microsoft Excel addin.

## Installation

Windows:

```sh
pip install geolab
```

## Usage example

```py
>>> from geolab import soil_classifier

# element in data should be arranged as follows
# liquid limit, plastic limit, plasticity index, fines, sand, gravel
>>> data = [34.1, 21.1, 13, 47.88, 37.84, 14.28]
>>> soil = soil_classifier.Soil(*data)
>>> soil.unified_classification
'SC'
>>> soil.aashto_classification
'A-6(3)'

```

<!-- ## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
``` -->

## Release History

-   0.1.0
    -   **rapid** development.

## Contributing

1. [Fork it](https://github.com/patrickboateng/geolab/fork)
2. Create your feature branch (`git checkout -b feature`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature`)
5. Create a new Pull Request

## Todo

-   [x] Soil Classifier
-   [ ] Bearing Capacity Analysis
-   [ ] Estimating Soil Engineering Parameters
-   [ ] Settlement Analysis
-   [ ] Modelling the behavior of Soils under loads using `FEM`

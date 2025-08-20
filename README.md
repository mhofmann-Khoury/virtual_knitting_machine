# virtual_knitting_machine

[![PyPI - Version](https://img.shields.io/pypi/v/virtual-knitting-machine.svg)](https://pypi.org/project/virtual-knitting-machine)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/virtual-knitting-machine.svg)](https://pypi.org/project/virtual-knitting-machine)

-----
## Description
A data structure representing the state and operations of a virtual V-Bed with sliders whole garment knitting machine based on the whole garment knitting machines made by [Shima Seiki](https://www.shimaseiki.com/product/knit/swg_n2/).

Additional details about the representation of these machines is available in ["KnitScript: A Domain-Specific Scripting Language for Advanced Machine Knitting"](https://doi.org/10.1145/3586183.3606789).
## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Credits](#credits)
- [License](#license)

## Installation

```console
pip install virtual-knitting-machine
```

## Credits
The design of this knitting machine data structure was created for the KnitScript Programming language described in the ACM publication ["KnitScript: A Domain-Specific Scripting Language for Advanced Machine Knitting"](https://doi.org/10.1145/3586183.3606789).

This virtual knitting machine renders a knit graph structure available in the ['knit-graphs'](https://pypi.org/project/knit-graphs/)
python package and described by Hofmann et al. in ["KnitPicking Texture: Programming and Modifying Complex Knitted Textures for Machine and Hand Knitting"](https://doi.org/10.1145/3332165.3347886).

## License

`virtual-knitting-machine` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

# Reconstruct Aspherix Bodies
Merge Aspherix bodies into OVITO particles

## Description
The [Aspherix](https://www.aspherix-dem.com/) DEM software can output concave particles as bodies composed of multiple convex sub-particles. OVITO can read this body information into a [`DataTable`](https://www.ovito.org/docs/current/python/modules/ovito_data.html#ovito.data.DataTable). This modifier can be used to post-process the data table and replace the convex sub-particles in the [`DataCollection`](https://www.ovito.org/docs/current/python/modules/ovito_data.html#ovito.data.DataCollection) with their concave counterparts.

Note: This modifier currently only works for mesh based particles. If you require multi-sphere particles please open a GitHub issue.

## Parameters 

| GUI name                 | Python name            | Description                                                      | Default Value                       |
|--------------------------|------------------------|------------------------------------------------------------------|-------------------------------------|
| **Static color**         | `body_color`           | Single solid color applied to each newly created particle.       | `(255 / 255, 102 / 255, 102 / 255)` |
| **Random colors**        | `random_color`         | Apply a random color to each unique body.                        | `False`                             |
| **Delete sub-particles** | `delete_sub_particles` | Delete the sub-particles originally found in the DataCollection. | `True`                              |

## Example
Seperate sub-particles after a normal file import:

![Example 01](examples/unmerged_sub-particles.png)

Merged bodies from the `Reconstruct Aspherix Bodies` modifier:

![Example 02](examples/merged_particles.png)

## Installation
- OVITO Pro [integrated Python interpreter](https://docs.ovito.org/python/introduction/installation.html#ovito-pro-integrated-interpreter):
  ```
  ovitos -m pip install --user git+https://github.com/ovito-org/ReconstructAspherixBodies.git
  ``` 
  The `--user` option is recommended and [installs the package in the user's site directory](https://pip.pypa.io/en/stable/user_guide/#user-installs).

- Other Python interpreters or Conda environments:
  ```
  pip install git+https://github.com/ovito-org/ReconstructAspherixBodies.git
  ```

## Technical information / dependencies
- Tested on OVITO version 3.11.0

## Contact
- Daniel Utt (utt@ovito.org)
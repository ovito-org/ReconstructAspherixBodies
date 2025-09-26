import json

import numpy as np
from ovito.io import import_file

from ReconstructAspherixBodies import ReconstructAspherixBodies


def compare_dicts(dict1, dict2, path=""):
    global results
    assert isinstance(dict1, dict) and isinstance(dict2, dict)
    for key in dict1:
        assert key in dict2
        if key in dict2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                compare_dicts(dict1[key], dict2[key], path + f"/{key}")
            else:
                assert np.allclose(np.ravel(dict1[key]), np.ravel(dict2[key]))
    for key in dict2:
        assert key in dict1


def test_ReconstructAspherixBodies():
    pipeline = import_file("facetted_convex_concave/aspherix_simulation.pvd")

    # Reconstruct Aspherix Bodies:
    pipeline.modifiers.append(
        ReconstructAspherixBodies(
            body_color=(0.9434348344802856, 0.5904631018638611, 0.365468829870224)
        )
    )

    data = pipeline.compute(1)
    result = {"particles": {}, "tables": {}}
    for key in data.particles:
        result["particles"][key] = np.asarray(data.particles[key])
    for key1 in data.tables:
        result["tables"][key1] = {}
        for key2 in data.tables[key1]:
            result["tables"][key1][key2] = np.asarray(data.tables[key1][key2])

    with open("tests/reference_data.json", "r") as f:
        reference = json.load(f)

    compare_dicts(result, reference)

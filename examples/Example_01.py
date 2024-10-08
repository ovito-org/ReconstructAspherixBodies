# Boilerplate code generated by OVITO Pro 3.11.0
from ovito.data import DataCollection, DataTable
from ovito.io import import_file
from ovito.vis import Viewport

from ReconstructAspherixBodies import ReconstructAspherixBodies


def main():
    # ==== Set up pipeline ==== #

    # Data import:
    pipeline = import_file(
        "https://gitlab.com/ovito-org/ovito-sample-data/-/raw/master/Aspherix/facetted_convex_concave/aspherix_simulation.pvd?ref_type=heads&inline=false"
    )

    # Manual modifications of the imported data objects:
    def modify_pipeline_input(frame: int, data: DataCollection):
        data.tables["bodies_"].plot_mode = DataTable.PlotMode.NoPlot

    pipeline.modifiers.append(modify_pipeline_input)

    # Reconstruct Aspherix Bodies:
    pipeline.modifiers.append(
        ReconstructAspherixBodies(
            body_color=(0.9434348344802856, 0.5904631018638611, 0.365468829870224)
        )
    )

    # ======= Set up visual elements ======= #

    # Configure visual elements for pipeline
    pipeline.compute(1).cell.vis.enabled = False
    pipeline.compute(1).particles.forces.vis.width = 0.0025
    pipeline.compute(1).particles.forces.vis.flat_shading = False
    pipeline.compute(1).particles.forces.vis.enabled = True

    # Add pipelines to scene
    pipeline.add_to_scene()

    data = pipeline.compute(1)
    res = {"particles": {}, "tables": {}}
    import json

    import numpy as np

    for key in data.particles:
        res["particles"][key] = np.array(data.particles[key]).tolist()
    for key in data.tables:
        res["tables"][key] = {}
        for k2 in data.tables[key]:
            res["tables"][key][k2] = np.array(data.tables[key][k2]).tolist()
    with open("reference_data.json", "w") as f:
        json.dump(res, f)

    # ========== Set up rendering ========== #

    # Viewport setup:
    vp = Viewport(
        type=Viewport.Type.Perspective,
        fov=0.610865238198,
        camera_dir=[0.882397702612611, 0.46586453850688697, -0.06591301985003879],
        camera_pos=[-0.5116441568573582, -0.2415602076674027, 0.08702696569330423],
    )

    # Rendering:
    vp.render_image(filename="image.png", size=(800, 600), frame=1)


if __name__ == "__main__":
    main()

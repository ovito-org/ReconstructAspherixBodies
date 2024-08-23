#### Reconstruct Aspherix Bodies ####
# Merge Aspherix bodies into OVITO particles.
import numpy as np
from ovito.data import DataCollection, TriangleMesh
from ovito.pipeline import ModifierInterface
from ovito.traits import Color
from ovito.vis import ParticlesVis
from scipy.spatial.transform import Rotation as R
from traits.api import Bool


class ReconstructAspherixBodies(ModifierInterface):
    body_color = Color(default=(255 / 255, 102 / 255, 102 / 255), label="Static color")
    random_color = Bool(False, label="Random colors")
    delete_sub_particles = Bool(True, label="Delete sub-particles")

    @staticmethod
    def create_body_from_meshes(data, bodies, body_index, indices):
        # --- Generate the mesh for the body combining the partial meshes of all particles that make up the body --- #
        # Data buffers
        combined_vertices = []
        combined_faces = []
        vertex_count = 0

        # Collect partial meshes and bring them in a unified orientation and position
        for index in indices:
            ptype_id = data.particles["Particle Type"][index]
            ptype = data.particles["Particle Type"].type_by_id(ptype_id)

            mesh = ptype.mesh
            rot = R.from_quat(data.particles["Orientation"][index])
            verts = rot.apply(mesh.get_vertices())
            combined_vertices.append(verts + data.particles["Position"][index])
            combined_faces.append(mesh.get_faces() + vertex_count)
            vertex_count += mesh.vertex_count

        # Combine mesh parts
        body_pos = bodies["Position"][body_index]
        verts = rot.inv().apply(np.vstack(combined_vertices))
        body_pos_rot = rot.inv().apply(body_pos)
        verts -= body_pos_rot

        combined_mesh = TriangleMesh()
        combined_mesh.set_vertices(verts)
        combined_mesh.set_faces(np.vstack(combined_faces))
        return combined_mesh

    @staticmethod
    def create_particle_type(data, body_type_id, color, combined_mesh=None):
        # --- Add a new particle type or return the existing one--- #
        t_name = f"body_{body_type_id}"

        # Return existing particle type
        if t := data.particles["Particle Type"].type_by_name(t_name, require=False):
            return t.id

        # Create a new particle type using the combined mesh
        if combined_mesh:
            t = data.particles_["Particle Type_"].add_type_name(t_name, data.particles)
            t.color = color
            t.radius = 1
            t.mesh = combined_mesh
            t.shape = ParticlesVis.Shape.Mesh
        else:
            raise NotImplementedError()
        return t.id

    def create_bodies(self, data, bindex, color):
        # Get body and particles
        bodies = data.tables["bodies"]
        body_id = bodies["Identifier"][bindex]
        indices = np.where(data.particles["body"] == body_id)[0]

        # --- Create combined mesh for this body --- #
        mesh = self.create_body_from_meshes(data, bodies, bindex, indices)
        # --- Add a new particle type or return the existing one--- #
        type_id = self.create_particle_type(
            data, bodies["Atom Type"][bindex], color, mesh
        )

        # --- Create one new particle for the body --- #
        pindex = data.particles_.add_particle(bodies["Position"][bindex])
        data.particles_["Particle Type_"][pindex] = type_id

        # Confirm that the orientation matches for all particles composing the body
        if not np.allclose(
            data.particles["Orientation"][indices[0]],
            data.particles["Orientation"][indices[1:]],
        ):
            raise ValueError("Not all particles in the body have the same Orientation")

        # Set the orientation
        data.particles_["Orientation_"][pindex] = data.particles["Orientation"][
            indices[0]
        ]

        # --- Copy data from the original particles and the bodies table to the newly created particle --- #
        # Data is copied when the property is present in the bodies table or all subparticles have the same value
        # Preference is given to the bodies table
        for key in data.particles:
            if key.endswith("_"):
                continue
            elif key == "Particle Identifier":
                data.particles_[f"{key}_"][pindex] = np.max(data.particles[key]) + 1
            elif key in bodies:
                data.particles_[f"{key}_"][pindex] = bodies[key][bindex]
            else:
                if np.allclose(
                    data.particles[key][indices[0]], data.particles[key][indices[1:]]
                ):
                    data.particles_[f"{key}_"][pindex] = data.particles[key][indices[0]]

    def modify(self, data: DataCollection, **kwargs):
        if not data.particles:
            raise RuntimeError("Particles object required")
        if "bodies" not in data.tables:
            raise RuntimeError("'bodies' table required")

        if self.delete_sub_particles:
            original_particles = data.particles.count

        if self.random_color:
            rng = np.random.default_rng(1323)

        for body_index in range(len(data.tables["bodies"]["Identifier"])):
            if self.random_color:
                color = rng.random(3)
            else:
                color = self.body_color
            # Create new bodies
            self.create_bodies(data, body_index, color)
            yield body_index / len(data.tables["bodies"]["Identifier"])

        if self.delete_sub_particles:
            # Mask and delete old sub-particles
            mask = np.ones(data.particles.count, dtype=bool)
            mask[original_particles:] = 0
            data.particles_.delete_elements(
                np.logical_and(mask, data.particles["body"] != -1)
            )

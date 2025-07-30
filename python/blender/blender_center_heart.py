import bpy
import mathutils


# Select all objects in the scene
bpy.ops.object.select_all(action='SELECT')

# Deselect unnecessary objects (type empty)
bpy.ops.object.select_by_type(type='EMPTY', action='DESELECT')

# Get selected objects
selected = [obj for obj in bpy.context.selected_objects]

# Compute the combined center of volume
total_volume = 0.0
weighted_centroid = mathutils.Vector((0.0, 0.0, 0.0))

for obj in selected:
    mesh = obj.to_mesh()
    mesh.transform(obj.matrix_world)
    center = mathutils.Vector((0.0, 0.0, 0.0))
    volume = 0.0

    for poly in mesh.polygons:
        verts = [mesh.vertices[i].co for i in poly.vertices]
        if len(verts) >= 3:
            # Use triangle fan to compute approximate volume and center
            for i in range(1, len(verts) - 1):
                v0, v1, v2 = verts[0], verts[i], verts[i + 1]
                tetra_volume = v0.cross(v1).dot(v2) / 6.0
                tri_center = (v0 + v1 + v2) / 4.0  # Coarse approx
                center += tri_center * tetra_volume
                volume += tetra_volume

    if abs(volume) > 1e-6:
        weighted_centroid += center
        total_volume += volume

    bpy.data.meshes.remove(mesh)

if total_volume != 0:
    combined_center = weighted_centroid / total_volume

    # Move all objects so the center moves to (0, 0, 0)
    for obj in selected:
        obj.location -= combined_center

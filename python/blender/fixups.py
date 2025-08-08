import bpy
import init


# Zero weights among selected meshes
def zero_weights():
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            for vg in obj.vertex_groups:
                for v in obj.data.vertices:
                    vg.add([v.index], 0.0, 'REPLACE')


# Add inverse bones to prevent normalization issues
def add_inverse_bones() -> bool:
    for component in init.HEART_COMPONENTS:
        print(f"\tAdding inverse bone for {component}...")

        obj = bpy.data.objects.get(component)
        if not obj:
            print(f"Warning: Object '{component}' not found in the scene.")
            return False

        # If this script has already been ran, update the vertex group and continue
        if f"{component}_inverse" in obj.vertex_groups:
            print(f"\tInverse bone for {component} found, updating vertex group...")
            vg_bone = obj.vertex_groups[f"{component}_bone"]
            vg_inverse = obj.vertex_groups[f"{component}_inverse"]
            _invert(obj, vg_bone, vg_inverse)
            continue

        # Add a bone to the armature
        armature = bpy.data.objects.get(f"{component}_armature")
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        armature_data = armature.data
        bone = armature_data.edit_bones.new(f"{component}_inverse")
        bone.head = (0, 0, 5)  # out of the way -- this does not matter since we won't scale the bone
        bone.tail = (0, 0, 6)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Duplicate the <component>_bone vertex group as <component>_inverse, then invert the new group
        if f"{component}_bone" in obj.vertex_groups:
            vg_bone = obj.vertex_groups[f"{component}_bone"]
            vg_inverse = obj.vertex_groups.new(name=f"{component}_inverse")
            _invert(obj, vg_bone, vg_inverse)
        else:
            print(f"Error: No vertex group found for component '{component}'")
            return False

        # Add inverse armature modifier to the mesh
        armature_inverse_modifier = obj.modifiers.new(name=f"{component}_armature_inverse", type='ARMATURE')
        armature_inverse_modifier.object = armature
        armature_inverse_modifier.use_vertex_groups = True
        armature_inverse_modifier.use_bone_envelopes = False
        armature_inverse_modifier.vertex_group = f"{component}_inverse"

    # Return true
    return True


def _invert(obj, vg_bone, vg_inverse):
    for vertex in obj.data.vertices:
        try:
            weight = vg_bone.weight(vertex.index)
            vg_inverse.add([vertex.index], 1.0 - weight, 'REPLACE')
        except RuntimeError: # vertex not in vertex group
                pass
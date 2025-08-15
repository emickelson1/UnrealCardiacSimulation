import bpy
import init
import mathutils

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

        # Add a bone to the armature as a child of the previous bone
        armature = bpy.data.objects.get(f"{component}_armature")
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        armature_data = armature.data
        main_bone = armature_data.edit_bones[0]

        inverse_bone = armature_data.edit_bones.new(f"{component}_inverse")
        inverse_bone.head = main_bone.head
        inverse_bone.tail = main_bone.head + (main_bone.tail - main_bone.head)/2
        main_bone.parent = inverse_bone
        
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
        

def correct_scale():
    # Read global unit scale
    unit_scale = bpy.context.scene.unit_settings.scale_length

    # If the scale correction fix has already been applied, return
    if unit_scale == 0.01:
        print("Unit scale is already 0.01. Skipping scale correction.")
        return False
    
    # Set unit scale for UE5 compatability
    bpy.context.scene.unit_settings.scale_length = 0.01

    # Scale meshes and armatures by 100x
    _scale_all_of_type('MESH', 100.0)
    _scale_all_of_type('ARMATURE', 100.0)

    return True


def _scale_all_of_type(type, scale=100.0):
    # Reset mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get objs of type
    objs = [obj for obj in bpy.data.objects if obj.type == type]
    if not objs:
        print(f"Error: no objs of type {type}")
        return
    for obj in objs: 
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    # Edit objs
    if type == 'MESH':
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.resize(value=(scale, scale, scale))
    elif type == 'ARMATURE':
        # multiply each bone's transform by 100
        for obj in objs:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            armature = bpy.context.object
            if armature and armature.type == 'ARMATURE' and bpy.context.mode == 'EDIT_ARMATURE':
                for bone in armature.data.edit_bones:
                    if bone.select:
                        bone.head *= 100
                        bone.tail *= 100
  
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

import bpy
import mathutils

import init

# The collection where armatures will be stored
ARMATURE_COLLECTION_NAME = "armature"

# Scale down the bone size for clearer visuals
BONE_APPEARANCE_SCALE = .5


def main():
    """Create bones and armatures for meshes in the scene, then link to the animation drivers."""
    global ARMATURE_COLLECTION_NAME

    # Ensure armature collection exists
    if not bpy.data.collections.get(ARMATURE_COLLECTION_NAME):
        armature_collection = bpy.data.collections.new(ARMATURE_COLLECTION_NAME)
        bpy.context.scene.collection.children.link(armature_collection)

    # Handle armature for each heart component
    for component in init.HEART_COMPONENTS:
        # Select component
        obj = bpy.data.objects.get(component)
        if not obj:
            print(f"Warning: Object '{component}' not found in the scene.")
            continue
        bpy.context.view_layer.objects.active = obj

        # Initialize armature obj
        armature_data = bpy.data.armatures.new(f"{component}_armature_data")
        armature_obj = bpy.data.objects.new(f"{component}_armature", object_data=armature_data)

        # Initialize armature modifier on mesh
        armature_mod = obj.modifiers.new(name='armature', type='ARMATURE')
        armature_mod.object = armature_obj

        # Add armature to collection
        armature_collection = bpy.data.collections.get(ARMATURE_COLLECTION_NAME)
        if armature_collection and armature_obj.name not in armature_collection.objects:
            armature_collection.objects.link(armature_obj)
        bpy.context.view_layer.objects.active = armature_obj

        # Unlink from other collections except the master scene collection and armature collection
        for collection in list(armature_obj.users_collection):
            if collection.name not in {ARMATURE_COLLECTION_NAME, bpy.context.scene.collection.name}:
                collection.objects.unlink(armature_obj)

        # Create a bone for the armature
        bpy.data.objects[armature_obj.name].select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bone = armature_data.edit_bones.new(f"{component}_bone")

        # Set bone head and tail
        bone_head = get_closest_vertex(component, obj.location)
        bone.head = bone_head
        bone.tail = compose_bone_tail(component, bone_head)

        # If a vertex group exists for the obj, assign the armature modifier bone group to that vertex group
        if obj.vertex_groups.active:
            armature_mod.vertex_group = obj.vertex_groups.active.name
            armature_mod.use_vertex_groups = True
            armature_mod.use_bone_envelopes = False

            # Assign all vertices in the active vertex group to the bone with full weight
            vg = obj.vertex_groups.active
            for v in obj.data.vertices:
                vg.add([v.index], 1.0, 'REPLACE')
            # print(f"Assigned bone '{bone.name}' to vertex group '{obj.vertex_groups.active.name}'")
        else:
            print(f"Warning: No vertex group found for component '{component}'. Skipping bone assignment.")

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def get_forward_vector() -> mathutils.Vector:
    """Get the forward vector of the heart. This is the vector that points from the atria to the ventricles."""

    # Function for getting a component's furthest vertex from the origin
    def get_furthest_vertex(component: str) -> mathutils.Vector:
        obj = bpy.data.objects.get(component)
        if not obj:
            print(f"Warning: Object '{component}' not found in the scene.")
            return mathutils.Vector((0.0, 0.0, 0.0))

        # Get the furthest vertex from the origin
        furthest_location = mathutils.Vector((0.0, 0.0, 0.0))
        furthest_dist = float('-inf')
        for v in obj.data.vertices:
            world_co = obj.matrix_world @ v.co  # world coordinates
            dist = world_co.length
            if dist > furthest_dist:
                furthest_dist = dist
                furthest_location = world_co

        return furthest_location

    # Get the components
    lv_vector  = get_furthest_vertex("lv")
    rv_vector = get_furthest_vertex("rv")
    la_vector = get_furthest_vertex("la")
    pa_vector = get_furthest_vertex("pa")
    
    # Calculate the forward vector
    # Forward vector: from atria (la, pa) to ventricles (rv, lv)
    atria_center = (la_vector + pa_vector) / 2
    ventricle_center = (lv_vector + rv_vector) / 2
    forward_vector = ventricle_center - atria_center
    forward_vector.normalize()
    return forward_vector


def get_closest_vertex(component: str, point: mathutils.Vector) -> mathutils.Vector:
    """Get the closest vertex on the component to the point"""

    # Define object
    obj = bpy.data.objects.get(component)
    if not obj:
        print(f"Warning: Object '{component}' not found in the scene.")
        return mathutils.Vector((0.0, 0.0, 0.0))

    # Get closest vertex
    closest_location = mathutils.Vector((0.0, 0.0, 0.0))
    closest_dist = float('inf')
    for v in obj.data.vertices:
        world_co = obj.matrix_world @ v.co  # world coordinates instead of local coordinates
        dist = (point - world_co).length
        if dist < closest_dist:
            closest_dist = dist
            closest_location = world_co

    # Error checks
    if closest_dist == float('inf'):
        print(f"Warning: No vertices found in object '{component}'.")
        return mathutils.Vector((0.0, 0.0, 0.0))
    if closest_location.length == 0.0:
        print(f"Warning: Closest vertex in object '{component}' is at the origin.")

    return closest_location


def compose_bone_tail(component: str, bone_head: mathutils.Vector) -> mathutils.Vector:
    """Compose the tail of the bone based on the head and override vectors."""
    global BONE_APPEARANCE_SCALE

    # Get the component object
    obj = bpy.data.objects.get(component)
    if not obj:
        print(f"Warning: Object '{component}' not found in the scene.")
        return bone_head
    
    # Get forward vector
    forward_vector = get_forward_vector()

    # Get vector towards organ as cross product of forward vector
    towards_organ_vector = forward_vector.cross(mathutils.Vector((0, 0, 1))).normalized()
    if ((obj.location + towards_organ_vector).length < (obj.location - towards_organ_vector).length):
        towards_organ_vector = -towards_organ_vector

    # Initialize override vectors for specific components
    override_vectors = {
        "svc": mathutils.Vector((0.0, 0.0, 1.0)),  # Superior vena cava points up
        "a": mathutils.Vector((0.0, 0.0, 1.0)),  # Aorta points up
        "pa": -get_forward_vector()  # Pulmonary artery points away from the ventricles
    }

    # Compose bone tail vector
    bone_tail = bone_head
    if component in override_vectors:
        bone_tail += override_vectors[component] * BONE_APPEARANCE_SCALE
    else:
        bone_tail += bone_head * mathutils.Vector((1, 1, .6)) * BONE_APPEARANCE_SCALE
        bone_tail += (towards_organ_vector * mathutils.Vector((.2, .2, 0))).normalized() * BONE_APPEARANCE_SCALE
    return bone_tail


if __name__ == "__main__":
    main()
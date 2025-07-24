import bpy

def bake_obj_to_shape_keys(obj, start, end, step=1, name_prefix="F"):
    """Bake evaluated mesh deformation to one shape key per frame, keyframed."""
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Ensure mesh object
    if obj.type != 'MESH':
        print(f"Skipping {obj.name}: not a mesh")
        return

    # Ensure Basis exists
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)

    # Cache vertex count of first evaluated mesh to enforce constant topology
    scene.frame_set(start)
    eval_obj = obj.evaluated_get(depsgraph)
    me0 = eval_obj.to_mesh()
    vcount = len(me0.vertices)
    eval_obj.to_mesh_clear()

    # Wipe any existing animation on shape keys (optional)
    sk = obj.data.shape_keys
    if sk.animation_data and sk.animation_data.action:
        sk.animation_data_clear()

    # Disable all keys during baking
    for kb in obj.data.shape_keys.key_blocks:
        kb.value = 0.0

    print(f"Baking {obj.name}: frames {start}-{end} (step {step}), {vcount} verts")

    for f in range(start, end + 1, step):
        scene.frame_set(f)
        eval_obj = obj.evaluated_get(depsgraph)
        me = eval_obj.to_mesh()

        if len(me.vertices) != vcount:
            eval_obj.to_mesh_clear()
            raise RuntimeError(
                f"Topology changed on frame {f} for {obj.name} "
                f"({len(me.vertices)} vs {vcount}). Aborting."
            )

        key = obj.shape_key_add(name=f"{name_prefix}{f:04d}", from_mix=False)
        # Copy verts
        for v_src, v_key in zip(me.vertices, key.data):
            v_key.co = v_src.co

        eval_obj.to_mesh_clear()

        # Animate: key ON at f, OFF at f+step
        # Zero all first to avoid residual influence
        for kb in obj.data.shape_keys.key_blocks:
            kb.value = 0.0

        key.value = 1.0
        key.keyframe_insert("value", frame=f)
        key.value = 0.0
        key.keyframe_insert("value", frame=f + step)

    # Make interpolation CONSTANT (stepped)
    action = obj.data.shape_keys.animation_data.action if obj.data.shape_keys.animation_data else None
    if action:
        for fcurve in action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'CONSTANT'

    print(f"Done baking {obj.name}")

def main():
    scene = bpy.context.scene
    start, end = scene.frame_start, scene.frame_end
    step = 1  # change if you want to sample every N frames

    objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    if not objs:
        print("No mesh objects selected.")
        return

    for obj in objs:
        bake_obj_to_shape_keys(obj, start, end, step=step, name_prefix="F")

if __name__ == "__main__":
    main()

import bpy


bl_info = {
    "name" : "Heart Model Tools",
    "author" : "Elijah Mickelson",
    "version" : (1, 0, 0),
    "blender" : (4, 4, 3),
    "location" : "View3d > Cardiac",
    "warning" : "",
    "wiki_url" : "",
    "category" : ""
}


# Properties for the UI
class MyProperties(bpy.types.PropertyGroup):
    export_relative_path: bpy.props.StringProperty(name = "Export Path", description = "Path to export the model to, relative to the project root file", default = "assets/heart_fbx_models", maxlen = 128, subtype = 'DIR_PATH')
    export_name: bpy.props.StringProperty(name = "Export Name", description = "Name of the exported file (without extension)", default = "", maxlen = 32, subtype = 'FILE_NAME')
    export_format: bpy.props.EnumProperty(name = "Export Format", description = "File format to export the model as", items = [('FBX Discontinuous', "FBX Discontinuous", "Autodesk FBX format (static meshes)"), ('FBX Continuous', "FBX Continuous", "Autodesk FBX format (animated skeletal mesh)"), ('ABC', "ABC", "Alembic ABC format")], default = 'FBX Discontinuous')


# Main UI panel for export
class CARDIAC_PT_main_panel(bpy.types.Panel):
    bl_label = "Export Model"
    bl_idname = "CARDIAC_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cardiac"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "export_relative_path")
        layout.prop(mytool, "export_name")
        layout.prop(mytool, "export_format")
        layout.operator("cardiac.zero_weights", text="Zero Weights")
        layout.operator("cardiac.add_inverse_bones", text="Add Inverse Bones")
        layout.operator("cardiac.export_model", text="Export Model")


# Operator: export
class CARDIAC_OT_export(bpy.types.Operator):
    bl_label = "Export Model"
    bl_idname = "cardiac.export_model"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        print(f"Exporting model to {mytool.export_relative_path}/{mytool.export_name}.{mytool.export_format}")

        import export
        export.export_heart(str(mytool.export_relative_path), str(mytool.export_name), str(mytool.export_format))
        return {'FINISHED'}


# Operator: zero weights
class CARDIAC_OT_zero_weights(bpy.types.Operator):
    bl_label = "Zero Weights"
    bl_idname = "cardiac.zero_weights"

    def execute(self, context):
        print("Zeroing weights for selected meshes...")
        import fixups
        fixups.zero_weights()
        print("Zeroing weights for selected meshes complete.")
        return {'FINISHED'}


# Operator: add inverse bones
class CARDIAC_OT_add_inverse_bones(bpy.types.Operator):
    bl_label = "Add Inverse Bones"
    bl_idname = "cardiac.add_inverse_bones"

    def execute(self, context):
        print("Adding inverse bones to selected meshes...")
        import fixups
        success = fixups.add_inverse_bones()
        if success:
            print("Inverse bones added successfully.")
        else:
            print("Failed to add inverse bones.")
        return {'FINISHED'}


# Operator: fix unit scale
class CARDIAC_OT_fix_unit_scale(bpy.types.Operator):
    bl_label = "Fix Unit Scale"
    bl_idname = "cardiac.fix_unit_scale"

    def execute(self, context):
        print("Fixing unit scale...")
        import fixups
        success = fixups.correct_scale()
        if success:
            print("Unit scale fixed successfully.")
        else:
            print("Failed to fix unit scale.")
        return {'FINISHED'}




classes = [MyProperties, CARDIAC_PT_main_panel, CARDIAC_OT_export, CARDIAC_OT_zero_weights, CARDIAC_OT_add_inverse_bones]

def register():
    #bpy.app.handlers.frame_change_post.append(frame_change_handler)
    for cls in classes:
        bpy.utils.register_class(cls)
        
        bpy.types.Scene.my_tool = bpy.props.PointerProperty(type = MyProperties)
 
def unregister():
    #bpy.app.handlers.frame_change_post.remove(frame_change_handler)
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
        del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()

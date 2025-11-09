"""
Blender Printable Labels
========================

A Blender addon for creating 3D printable organization labels with mounting holes.

GitHub: https://github.com/JonathanPorta/blender-printable-labels

Installation:
    1. Save this file as blender_printable_labels.py
    2. Open Blender > Edit > Preferences > Add-ons
    3. Click "Install" and select this file
    4. Enable the addon by checking the checkbox
    
Usage:
    1. Open 3D Viewport
    2. Press 'N' to open sidebar
    3. Click on "Label Maker" tab
    4. Enter your settings
    5. Click "Create Label" or "Create Batch"
"""

bl_info = {
    "name": "Blender Printable Labels",
    "author": "Jonathan Porta",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Label Maker",
    "description": "Create 3D printable organization labels with mounting holes",
    "doc_url": "https://github.com/JonathanPorta/blender-printable-labels",
    "category": "Add Mesh",
}

import bpy
import bmesh
import struct
import os
from bpy.props import (
    StringProperty,
    FloatProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    IntProperty
)
from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
)


# ==============================================================================
# CORE FUNCTIONS
# ==============================================================================

def write_stl_binary(filepath, mesh):
    """Write a mesh to an STL file in binary format."""
    with open(filepath, 'wb') as f:
        f.write(b'Binary STL created by Blender' + b' ' * 51)
        num_tris = len(mesh.loop_triangles)
        f.write(struct.pack('<I', num_tris))
        
        for tri in mesh.loop_triangles:
            normal = tri.normal
            f.write(struct.pack('<fff', normal.x, normal.y, normal.z))
            
            for loop_index in tri.loops:
                vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
                co = vertex.co
                f.write(struct.pack('<fff', co.x, co.y, co.z))
            
            f.write(struct.pack('<H', 0))


def create_label_mesh(context, props):
    """Create a label mesh based on properties."""
    
    z_pos = props.base_thickness / 2
    
    # 1. Create base
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, z_pos))
    base = context.active_object
    clean_name = props.label_text.replace(" ", "_").replace("/", "_")
    base.name = f"Label_{clean_name}"
    
    base.scale = (props.base_width / 2, props.base_height / 2, props.base_thickness / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 2. Add text
    text_z = props.base_thickness + (props.text_extrude / 2)
    bpy.ops.object.text_add(location=(0, 0, text_z))
    text_obj = context.active_object
    text_obj.data.body = props.label_text
    text_obj.data.size = props.text_size
    text_obj.data.align_x = 'CENTER'
    text_obj.data.align_y = 'CENTER'
    text_obj.data.extrude = props.text_extrude
    
    bpy.ops.object.convert(target='MESH')
    
    # 3. Mirror text
    if props.mirror_text:
        mirror = text_obj.modifiers.new(name="Mirror", type='MIRROR')
        mirror.use_axis[0] = False
        mirror.use_axis[1] = True
        mirror.use_axis[2] = False
        bpy.ops.object.modifier_apply(modifier="Mirror")
    
    # 4. Join text to base
    bpy.ops.object.select_all(action='DESELECT')
    text_obj.select_set(True)
    base.select_set(True)
    context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    # 5. Create mounting holes
    half_width = props.base_width / 2
    half_height = props.base_height / 2
    hole_radius = props.hole_diameter / 2
    
    hole_positions = [
        (-half_width + props.hole_inset, half_height - props.hole_inset, z_pos, "Hole_Left_Top"),
        (-half_width + props.hole_inset, -half_height + props.hole_inset, z_pos, "Hole_Left_Bottom"),
        (half_width - props.hole_inset, half_height - props.hole_inset, z_pos, "Hole_Right_Top"),
        (half_width - props.hole_inset, -half_height + props.hole_inset, z_pos, "Hole_Right_Bottom")
    ]
    
    cylinders = []
    for x, y, z, name in hole_positions:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=hole_radius,
            depth=props.base_thickness * 2,
            location=(x, y, z)
        )
        cyl = context.active_object
        cyl.name = name
        cylinders.append(cyl)
    
    # 6. Apply boolean modifiers
    if props.apply_booleans:
        for cyl in cylinders:
            bpy.ops.object.select_all(action='DESELECT')
            base.select_set(True)
            context.view_layer.objects.active = base
            
            bool_mod = base.modifiers.new(name=f"Boolean_{cyl.name}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = cyl
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        
        if props.delete_cylinders:
            bpy.ops.object.select_all(action='DESELECT')
            for cyl in cylinders:
                cyl.select_set(True)
            bpy.ops.object.delete()
    
    return base


def export_label_stl(obj, filepath):
    """Export a label object to STL."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    mesh.calc_loop_triangles()
    
    write_stl_binary(filepath, mesh)
    obj_eval.to_mesh_clear()


# ==============================================================================
# PROPERTY GROUPS
# ==============================================================================

class LabelGeneratorProperties(PropertyGroup):
    """Properties for label generation."""
    
    # Label text
    label_text: StringProperty(
        name="Label Text",
        description="Text to display on the label",
        default="My Label"
    )
    
    # Base dimensions
    base_width: FloatProperty(
        name="Width",
        description="Width of the label base in mm",
        default=50.0,
        min=10.0,
        max=200.0,
        unit='LENGTH'
    )
    
    base_height: FloatProperty(
        name="Height",
        description="Height of the label base in mm",
        default=12.5,
        min=5.0,
        max=100.0,
        unit='LENGTH'
    )
    
    base_thickness: FloatProperty(
        name="Thickness",
        description="Thickness of the label base in mm",
        default=1.25,
        min=0.5,
        max=10.0,
        unit='LENGTH'
    )
    
    # Text properties
    text_size: FloatProperty(
        name="Text Size",
        description="Size of the text in mm",
        default=3.0,
        min=0.5,
        max=20.0,
        unit='LENGTH'
    )
    
    text_extrude: FloatProperty(
        name="Text Depth",
        description="Extrusion depth of the text in mm",
        default=0.5,
        min=0.1,
        max=5.0,
        unit='LENGTH'
    )
    
    mirror_text: BoolProperty(
        name="Mirror Text",
        description="Mirror text on Y-axis for readability from both sides",
        default=True
    )
    
    # Hole properties
    hole_diameter: FloatProperty(
        name="Hole Diameter",
        description="Diameter of mounting holes in mm",
        default=2.5,
        min=1.0,
        max=20.0,
        unit='LENGTH'
    )
    
    hole_inset: FloatProperty(
        name="Hole Inset",
        description="Distance from edges to hole centers in mm",
        default=3.0,
        min=1.0,
        max=20.0,
        unit='LENGTH'
    )
    
    # Boolean options
    apply_booleans: BoolProperty(
        name="Apply Booleans",
        description="Apply boolean modifiers to create holes",
        default=True
    )
    
    delete_cylinders: BoolProperty(
        name="Delete Cylinders",
        description="Delete cylinder objects after applying booleans",
        default=True
    )
    
    # Export options
    auto_export: BoolProperty(
        name="Auto Export STL",
        description="Automatically export to STL after creation",
        default=False
    )
    
    export_path: StringProperty(
        name="Export Path",
        description="Directory to export STL files",
        default="//labels/",
        subtype='DIR_PATH'
    )
    
    # Presets
    size_preset: EnumProperty(
        name="Size Preset",
        description="Common size presets for labels",
        items=[
            ('CUSTOM', "Custom", "Custom dimensions"),
            ('CLOSET', "Closet Standard", "50mm x 12.5mm - Standard closet label"),
            ('DRAWER', "Drawer Small", "40mm x 10mm - Small drawer label"),
            ('GARAGE', "Garage Large", "75mm x 20mm - Large garage label"),
            ('WIDE', "Wide", "100mm x 15mm - Wide label"),
        ],
        default='CLOSET',
    )


class BatchLabelItem(PropertyGroup):
    """Single label item for batch creation."""
    
    label_text: StringProperty(
        name="Label Text",
        description="Text for this label",
        default=""
    )
    
    enabled: BoolProperty(
        name="Enabled",
        description="Include this label in batch creation",
        default=True
    )


class BatchLabelProperties(PropertyGroup):
    """Properties for batch label creation."""
    
    labels: CollectionProperty(type=BatchLabelItem)
    active_index: IntProperty()


# ==============================================================================
# OPERATORS
# ==============================================================================

class OBJECT_OT_create_label(Operator):
    """Create a single printable label"""
    bl_idname = "object.create_printable_label"
    bl_label = "Create Label"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.label_generator
        
        # Apply preset if not custom
        if props.size_preset == 'CLOSET':
            props.base_width = 50.0
            props.base_height = 12.5
            props.text_size = 3.0
        elif props.size_preset == 'DRAWER':
            props.base_width = 40.0
            props.base_height = 10.0
            props.text_size = 2.5
        elif props.size_preset == 'GARAGE':
            props.base_width = 75.0
            props.base_height = 20.0
            props.text_size = 5.0
        elif props.size_preset == 'WIDE':
            props.base_width = 100.0
            props.base_height = 15.0
            props.text_size = 4.0
        
        # Create the label
        label = create_label_mesh(context, props)
        
        # Export if enabled
        if props.auto_export:
            filename = props.label_text.replace(" ", "_") + ".stl"
            filepath = bpy.path.abspath(props.export_path + filename)
            export_label_stl(label, filepath)
            self.report({'INFO'}, f"Label created and exported to {filepath}")
        else:
            self.report({'INFO'}, f"Label '{props.label_text}' created")
        
        return {'FINISHED'}


class OBJECT_OT_create_batch_labels(Operator):
    """Create multiple labels from the batch list"""
    bl_idname = "object.create_batch_printable_labels"
    bl_label = "Create Batch"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.label_generator
        batch_props = context.scene.batch_labels
        
        created_count = 0
        for item in batch_props.labels:
            if item.enabled and item.label_text.strip():
                # Temporarily set the label text
                original_text = props.label_text
                props.label_text = item.label_text
                
                # Create label
                label = create_label_mesh(context, props)
                
                # Export if enabled
                if props.auto_export:
                    filename = item.label_text.replace(" ", "_") + ".stl"
                    filepath = bpy.path.abspath(props.export_path + filename)
                    export_label_stl(label, filepath)
                
                created_count += 1
                
                # Restore original text
                props.label_text = original_text
        
        self.report({'INFO'}, f"Created {created_count} labels")
        return {'FINISHED'}


class OBJECT_OT_add_batch_label(Operator):
    """Add a new label to the batch list"""
    bl_idname = "object.add_batch_printable_label"
    bl_label = "Add Label"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        batch_props = context.scene.batch_labels
        item = batch_props.labels.add()
        item.label_text = f"Label {len(batch_props.labels)}"
        batch_props.active_index = len(batch_props.labels) - 1
        return {'FINISHED'}


class OBJECT_OT_remove_batch_label(Operator):
    """Remove selected label from the batch list"""
    bl_idname = "object.remove_batch_printable_label"
    bl_label = "Remove Label"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        batch_props = context.scene.batch_labels
        if batch_props.labels:
            batch_props.labels.remove(batch_props.active_index)
            batch_props.active_index = min(batch_props.active_index, len(batch_props.labels) - 1)
        return {'FINISHED'}


class OBJECT_OT_clear_labels(Operator):
    """Delete all label objects from the scene"""
    bl_idname = "object.clear_printable_labels"
    bl_label = "Clear All Labels"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        objects_to_delete = [obj for obj in bpy.data.objects 
                            if obj.name.startswith("Label_") or obj.name.startswith("Hole_")]
        
        if objects_to_delete:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects_to_delete:
                obj.select_set(True)
            bpy.ops.object.delete()
            self.report({'INFO'}, f"Deleted {len(objects_to_delete)} label objects")
        else:
            self.report({'INFO'}, "No labels to delete")
        
        return {'FINISHED'}


class OBJECT_OT_load_preset_labels(Operator):
    """Load preset closet labels into batch list"""
    bl_idname = "object.load_preset_printable_labels"
    bl_label = "Load Closet Presets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        batch_props = context.scene.batch_labels
        
        # Clear existing
        batch_props.labels.clear()
        
        # Add preset labels
        preset_labels = [
            "EMS Shirts", "EMS Pants", "Work Shirts", "Work Pants",
            "Cold Weather", "Golf Shirts", "Dress Shirts",
            "Regular T Shirts", "Regular Pants", "Dresses"
        ]
        
        for text in preset_labels:
            item = batch_props.labels.add()
            item.label_text = text
            item.enabled = True
        
        self.report({'INFO'}, f"Loaded {len(preset_labels)} preset labels")
        return {'FINISHED'}


# ==============================================================================
# UI PANELS
# ==============================================================================

class VIEW3D_PT_label_generator(Panel):
    """Main panel for label generation"""
    bl_label = "Label Generator"
    bl_idname = "VIEW3D_PT_printable_label_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Label Maker"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.label_generator
        
        # Label text
        box = layout.box()
        box.label(text="Label Text:", icon='FONT_DATA')
        box.prop(props, "label_text", text="")
        
        # Size preset
        box = layout.box()
        box.label(text="Size Preset:", icon='PRESET')
        box.prop(props, "size_preset", text="")
        
        # Dimensions
        box = layout.box()
        box.label(text="Dimensions:", icon='SHADING_BBOX')
        col = box.column(align=True)
        col.prop(props, "base_width")
        col.prop(props, "base_height")
        col.prop(props, "base_thickness")
        
        # Text settings
        box = layout.box()
        box.label(text="Text Settings:", icon='SMALL_CAPS')
        col = box.column(align=True)
        col.prop(props, "text_size")
        col.prop(props, "text_extrude")
        col.prop(props, "mirror_text")
        
        # Hole settings
        box = layout.box()
        box.label(text="Mounting Holes:", icon='MESH_CIRCLE')
        col = box.column(align=True)
        col.prop(props, "hole_diameter")
        col.prop(props, "hole_inset")
        
        # Options
        box = layout.box()
        box.label(text="Options:", icon='MODIFIER')
        col = box.column(align=True)
        col.prop(props, "apply_booleans")
        col.prop(props, "delete_cylinders")
        
        # Export settings
        box = layout.box()
        box.label(text="Export:", icon='EXPORT')
        col = box.column(align=True)
        col.prop(props, "auto_export")
        if props.auto_export:
            col.prop(props, "export_path")
        
        # Create button
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("object.create_printable_label", icon='ADD')


class VIEW3D_PT_batch_labels(Panel):
    """Panel for batch label creation"""
    bl_label = "Batch Creation"
    bl_idname = "VIEW3D_PT_printable_batch_labels"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Label Maker"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        batch_props = context.scene.batch_labels
        
        # Preset button
        row = layout.row()
        row.operator("object.load_preset_printable_labels", icon='PRESET')
        
        # List controls
        row = layout.row()
        row.template_list("UI_UL_list", "batch_labels", batch_props, "labels",
                         batch_props, "active_index", rows=8)
        
        col = row.column(align=True)
        col.operator("object.add_batch_printable_label", icon='ADD', text="")
        col.operator("object.remove_batch_printable_label", icon='REMOVE', text="")
        
        # Edit selected item
        if batch_props.labels and batch_props.active_index < len(batch_props.labels):
            item = batch_props.labels[batch_props.active_index]
            box = layout.box()
            box.prop(item, "label_text", text="Text")
            box.prop(item, "enabled", text="Include in Batch")
        
        # Create batch button
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("object.create_batch_printable_labels", icon='STICKY_UVS_LOC')


class VIEW3D_PT_label_utilities(Panel):
    """Utility panel for label management"""
    bl_label = "Utilities"
    bl_idname = "VIEW3D_PT_printable_label_utilities"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Label Maker"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Scene Management:", icon='OUTLINER')
        box.operator("object.clear_printable_labels", icon='TRASH')
        
        # Info
        box = layout.box()
        box.label(text="Info:", icon='INFO')
        label_count = len([obj for obj in bpy.data.objects if obj.name.startswith("Label_")])
        box.label(text=f"Labels in scene: {label_count}")


# ==============================================================================
# REGISTRATION
# ==============================================================================

classes = (
    LabelGeneratorProperties,
    BatchLabelItem,
    BatchLabelProperties,
    OBJECT_OT_create_label,
    OBJECT_OT_create_batch_labels,
    OBJECT_OT_add_batch_label,
    OBJECT_OT_remove_batch_label,
    OBJECT_OT_clear_labels,
    OBJECT_OT_load_preset_labels,
    VIEW3D_PT_label_generator,
    VIEW3D_PT_batch_labels,
    VIEW3D_PT_label_utilities,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.label_generator = bpy.props.PointerProperty(type=LabelGeneratorProperties)
    bpy.types.Scene.batch_labels = bpy.props.PointerProperty(type=BatchLabelProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.label_generator
    del bpy.types.Scene.batch_labels


if __name__ == "__main__":
    register()

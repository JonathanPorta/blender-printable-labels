"""
Blender Printable Labels - Script Version
==========================================

A reusable script for creating 3D printable organization labels with mounting holes.

GitHub: https://github.com/JonathanPorta/blender-printable-labels

Usage in Blender:
    1. Open Blender's Text Editor
    2. Load this script or paste it in
    3. Modify the labels list at the bottom as needed
    4. Run the script (Alt+P or click Run Script)

Or use from Python console:
    >>> exec(open("/path/to/label_generator.py").read())
    >>> create_label("My Label", "/path/to/output.stl")
"""

import bpy
import bmesh
import struct
import os


def write_stl_binary(filepath, mesh):
    """
    Write a mesh to an STL file in binary format.
    
    Args:
        filepath (str): Full path to the output STL file
        mesh (bpy.types.Mesh): Blender mesh data to export
    """
    with open(filepath, 'wb') as f:
        # Header (80 bytes)
        f.write(b'Binary STL created by Blender' + b' ' * 51)
        
        # Number of triangles
        num_tris = len(mesh.loop_triangles)
        f.write(struct.pack('<I', num_tris))
        
        # Write each triangle
        for tri in mesh.loop_triangles:
            # Normal vector
            normal = tri.normal
            f.write(struct.pack('<fff', normal.x, normal.y, normal.z))
            
            # Three vertices
            for loop_index in tri.loops:
                vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
                co = vertex.co
                f.write(struct.pack('<fff', co.x, co.y, co.z))
            
            # Attribute byte count (unused)
            f.write(struct.pack('<H', 0))


def create_label(
    label_text,
    export_path=None,
    base_width=50.0,
    base_height=12.5,
    base_thickness=1.25,
    text_size=3.0,
    text_extrude=0.5,
    hole_diameter=2.5,
    hole_inset=3.0,
    mirror_text=True,
    apply_booleans=True,
    delete_cylinders=True
):
    """
    Create a 3D printable closet label with mounting holes.
    
    Args:
        label_text (str): Text to display on the label
        export_path (str, optional): Full path to export STL file. If None, doesn't export.
        base_width (float): Width of the label in mm (default: 50.0)
        base_height (float): Height of the label in mm (default: 12.5)
        base_thickness (float): Thickness of the label base in mm (default: 1.25)
        text_size (float): Text size in mm (default: 3.0)
        text_extrude (float): Text extrusion depth in mm (default: 0.5)
        hole_diameter (float): Diameter of mounting holes in mm (default: 2.5)
        hole_inset (float): Distance from edges to hole centers in mm (default: 3.0)
        mirror_text (bool): Whether to mirror text on Y-axis (default: True)
        apply_booleans (bool): Whether to apply boolean modifiers (default: True)
        delete_cylinders (bool): Whether to delete cylinder objects after boolean (default: True)
    
    Returns:
        bpy.types.Object: The created label object
        
    Example:
        >>> label = create_label("Kitchen", "/home/user/Kitchen.stl")
        >>> # Or without export:
        >>> label = create_label("Kitchen")
    """
    
    # Calculate z position (center of label thickness)
    z_pos = base_thickness / 2
    
    # 1. Create the base cube
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, z_pos))
    base = bpy.context.active_object
    
    # Create a clean object name
    clean_name = label_text.replace(" ", "_").replace("/", "_")
    base.name = f"Label_{clean_name}"
    
    # Scale to specified dimensions
    base.scale = (base_width / 2, base_height / 2, base_thickness / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 2. Add text
    text_z = base_thickness + (text_extrude / 2)
    bpy.ops.object.text_add(location=(0, 0, text_z))
    text_obj = bpy.context.active_object
    text_obj.data.body = label_text
    text_obj.data.size = text_size
    text_obj.data.align_x = 'CENTER'
    text_obj.data.align_y = 'CENTER'
    text_obj.data.extrude = text_extrude
    
    # Convert to mesh
    bpy.ops.object.convert(target='MESH')
    
    # 3. Mirror the text (if enabled)
    if mirror_text:
        mirror = text_obj.modifiers.new(name="Mirror", type='MIRROR')
        mirror.use_axis[0] = False  # Don't mirror X
        mirror.use_axis[1] = True   # Mirror Y
        mirror.use_axis[2] = False  # Don't mirror Z
        bpy.ops.object.modifier_apply(modifier="Mirror")
    
    # 4. Join text to base
    bpy.ops.object.select_all(action='DESELECT')
    text_obj.select_set(True)
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    # 5. Create mounting hole cylinders
    # Calculate hole positions based on dimensions and inset
    half_width = base_width / 2
    half_height = base_height / 2
    hole_radius = hole_diameter / 2
    
    hole_positions = [
        (-half_width + hole_inset, half_height - hole_inset, z_pos, "Hole_Left_Top"),
        (-half_width + hole_inset, -half_height + hole_inset, z_pos, "Hole_Left_Bottom"),
        (half_width - hole_inset, half_height - hole_inset, z_pos, "Hole_Right_Top"),
        (half_width - hole_inset, -half_height + hole_inset, z_pos, "Hole_Right_Bottom")
    ]
    
    cylinders = []
    for x, y, z, name in hole_positions:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=hole_radius,
            depth=base_thickness * 2,  # Make it tall enough to go through everything
            location=(x, y, z)
        )
        cyl = bpy.context.active_object
        cyl.name = name
        cylinders.append(cyl)
    
    # 6. Apply boolean modifiers to subtract cylinders (if enabled)
    if apply_booleans:
        for cyl in cylinders:
            bpy.ops.object.select_all(action='DESELECT')
            base.select_set(True)
            bpy.context.view_layer.objects.active = base
            
            bool_mod = base.modifiers.new(name=f"Boolean_{cyl.name}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = cyl
            
            # Apply the modifier
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        
        # 7. Delete the cylinder objects (if enabled)
        if delete_cylinders:
            bpy.ops.object.select_all(action='DESELECT')
            for cyl in cylinders:
                cyl.select_set(True)
            bpy.ops.object.delete()
    
    # 8. Export as STL (if path provided)
    if export_path:
        bpy.ops.object.select_all(action='DESELECT')
        base.select_set(True)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        # Get evaluated mesh and export
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = base.evaluated_get(depsgraph)
        mesh = obj_eval.to_mesh()
        
        # Calculate loop triangles
        mesh.calc_loop_triangles()
        
        # Write STL file
        write_stl_binary(export_path, mesh)
        
        # Clean up
        obj_eval.to_mesh_clear()
        
        print(f"✓ Exported: {os.path.basename(export_path)}")
    
    return base


def create_label_batch(labels, output_dir, **kwargs):
    """
    Create multiple labels at once.
    
    Args:
        labels (list): List of tuples (label_text, filename) or just label_text strings
        output_dir (str): Directory to save all STL files
        **kwargs: Additional arguments to pass to create_label()
    
    Returns:
        list: List of created label objects
        
    Example:
        >>> labels = [
        ...     ("Kitchen", "Kitchen.stl"),
        ...     ("Bathroom", "Bathroom.stl"),
        ...     "Living Room"  # filename will be auto-generated
        ... ]
        >>> create_label_batch(labels, "/home/user/labels/")
    """
    created_labels = []
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating {len(labels)} labels...")
    print("=" * 50)
    
    for item in labels:
        # Handle both tuple and string input
        if isinstance(item, tuple):
            label_text, filename = item
        else:
            label_text = item
            filename = f"{label_text.replace(' ', '_')}.stl"
        
        # Ensure filename has .stl extension
        if not filename.endswith('.stl'):
            filename += '.stl'
        
        export_path = os.path.join(output_dir, filename)
        
        try:
            label = create_label(label_text, export_path, **kwargs)
            created_labels.append(label)
            print(f"✓ Created: {label_text}")
        except Exception as e:
            print(f"✗ Failed: {label_text} - {str(e)}")
    
    print("=" * 50)
    print(f"Total: {len(created_labels)}/{len(labels)} labels created successfully")
    
    return created_labels


def clear_existing_labels():
    """
    Delete all existing label objects from the scene.
    Useful for cleaning up before creating new labels.
    """
    objects_to_delete = []
    for obj in bpy.data.objects:
        if obj.name.startswith("Label_") or obj.name.startswith("Hole_"):
            objects_to_delete.append(obj)
    
    if objects_to_delete:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_delete:
            obj.select_set(True)
        bpy.ops.object.delete()
        print(f"Deleted {len(objects_to_delete)} existing label objects")
    else:
        print("No existing labels to delete")


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    """
    Run this section when executing the script directly in Blender.
    Modify the labels list below to create your own custom labels.
    """
    
    # Clear any existing labels (optional)
    clear_existing_labels()
    
    # Define your labels
    # Format: (label_text, filename) or just label_text
    labels = [
        ("EMS Shirts", "EMS_Shirts.stl"),
        ("EMS Pants", "EMS_Pants.stl"),
        ("Work Shirts", "Work_Shirts.stl"),
        ("Work Pants", "Work_Pants.stl"),
        ("Cold Weather", "Cold_Weather.stl"),
        ("Golf Shirts", "Golf_Shirts.stl"),
        ("Dress Shirts", "Dress_Shirts.stl"),
        ("Regular T Shirts", "Regular_T_Shirts.stl"),
        ("Regular Pants", "Regular_Pants.stl"),
        ("Dresses", "Dresses.stl")
    ]
    
    # Output directory
    output_dir = "/mnt/user-data/outputs"
    
    # Create all labels with default settings
    created_labels = create_label_batch(labels, output_dir)
    
    # Alternative: Create a single label with custom settings
    # label = create_label(
    #     label_text="Custom Label",
    #     export_path="/path/to/Custom_Label.stl",
    #     base_width=60.0,           # Wider label
    #     base_height=15.0,          # Taller label
    #     text_size=4.0,             # Larger text
    #     hole_diameter=3.0,         # Bigger holes
    #     hole_inset=4.0             # Further from edges
    # )
    
    print("\n✓ Script completed successfully!")

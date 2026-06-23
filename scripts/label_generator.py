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
    >>> create_label(line1="My Label", export_path="/path/to/output.stl")
"""

import bpy
import bmesh
import struct
import os


def sanitize_filename(text):
    """
    Sanitize text for use in filenames.
    Removes or replaces characters that can cause issues in filenames.

    Args:
        text (str): Text to sanitize

    Returns:
        str: Sanitized filename-safe text
    """
    # Replace spaces with underscores
    text = text.replace(" ", "_")

    # Remove or replace problematic characters
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '|': '_',
        '(': '',
        ')': '',
        '[': '',
        ']': '',
        '{': '',
        '}': '',
        '&': 'and',
        '%': 'pct',
        '#': 'num',
        '@': 'at',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any other non-alphanumeric characters except underscore, dash, and dot
    text = ''.join(c for c in text if c.isalnum() or c in ('_', '-', '.'))

    # Remove leading/trailing underscores and collapse multiple underscores
    text = '_'.join(filter(None, text.split('_')))

    # Ensure it's not empty
    if not text:
        text = "label"

    return text


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
    line1="",
    line2="",
    line3="",
    line4="",
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
    Create a 3D printable label with up to 4 lines of text and mounting holes.

    Args:
        line1 (str): First line of text (required, or at least one line must be provided)
        line2 (str): Second line of text (optional)
        line3 (str): Third line of text (optional)
        line4 (str): Fourth line of text (optional)
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
        >>> # Single line
        >>> label = create_label("Kitchen", export_path="/home/user/Kitchen.stl")
        >>>
        >>> # Multiple lines
        >>> label = create_label("Zone 1", "Heat Only", "Main Floor", export_path="/home/user/Zone1.stl")
        >>>
        >>> # With keyword arguments
        >>> label = create_label(line1="Hot Water", line2="120°F", base_width=60.0)
    """

    # Calculate z position (center of label thickness)
    z_pos = base_thickness / 2

    # Collect all non-empty text lines
    lines = []
    if line1.strip():
        lines.append(line1.strip())
    if line2.strip():
        lines.append(line2.strip())
    if line3.strip():
        lines.append(line3.strip())
    if line4.strip():
        lines.append(line4.strip())

    if not lines:
        lines = ["Label"]  # Default if all empty

    # 1. Create the base cube
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, z_pos))
    base = bpy.context.active_object

    # Create a clean object name from first line
    clean_name = sanitize_filename(lines[0])
    base.name = f"Label_{clean_name}"

    # Scale to specified dimensions
    base.scale = (base_width / 2, base_height / 2, base_thickness / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # 2. Add text - multiple lines
    text_z = base_thickness + (text_extrude / 2)
    text_objects = []

    # Calculate vertical spacing between lines
    line_count = len(lines)
    line_spacing = text_size * 1.2  # 20% spacing between lines

    # Calculate starting Y position (centered vertically)
    if line_count > 1:
        start_y = (line_count - 1) * line_spacing / 2
    else:
        start_y = 0

    for i, line_text in enumerate(lines):
        # Calculate Y position for this line
        y_offset = start_y - (i * line_spacing)

        bpy.ops.object.text_add(location=(0, y_offset, text_z))
        text_obj = bpy.context.active_object
        text_obj.data.body = line_text
        text_obj.data.size = text_size
        text_obj.data.align_x = 'CENTER'
        text_obj.data.align_y = 'CENTER'
        text_obj.data.extrude = text_extrude

        # Convert to mesh
        bpy.ops.object.convert(target='MESH')

        # Mirror the text (if enabled)
        if mirror_text:
            mirror = text_obj.modifiers.new(name="Mirror", type='MIRROR')
            mirror.use_axis[0] = False  # Don't mirror X
            mirror.use_axis[1] = True   # Mirror Y
            mirror.use_axis[2] = False  # Don't mirror Z
            bpy.ops.object.modifier_apply(modifier="Mirror")

        text_objects.append(text_obj)

    # 3. Join all text objects to base
    bpy.ops.object.select_all(action='DESELECT')
    for text_obj in text_objects:
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
        labels (list): List of items. Each item can be:
            - A string (used as line1)
            - A tuple of (line1, filename)
            - A dictionary with kwargs like {'line1': 'A', 'line2': 'B', 'filename': 'a.stl'}
        output_dir (str): Directory to save all STL files
        **kwargs: Additional arguments to pass to create_label()

    Returns:
        list: List of created label objects

    Example:
        >>> labels = [
        ...     ("Kitchen", "Kitchen.stl"),
        ...     ("Bathroom", "Bathroom.stl"),
        ...     "Living Room",  # filename will be auto-generated
        ...     {"line1": "Hot Water", "line2": "120°F"}
        ... ]
        >>> create_label_batch(labels, "/home/user/labels/")
    """
    created_labels = []

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Creating {len(labels)} labels...")
    print("=" * 50)

    for item in labels:
        label_kwargs = {}
        filename = None

        # Handle dict, tuple and string input
        if isinstance(item, dict):
            label_kwargs = item.copy()
            if 'filename' in label_kwargs:
                filename = label_kwargs.pop('filename')
            # Extract line1 for logging
            label_text = label_kwargs.get('line1', 'Label')
        elif isinstance(item, tuple):
            label_text, filename = item
            label_kwargs['line1'] = label_text
            # Sanitize the provided filename (remove extension, sanitize, re-add extension)
            if filename.endswith('.stl'):
                filename = filename[:-4]
            filename = sanitize_filename(filename) + '.stl'
        else:
            label_text = str(item)
            label_kwargs['line1'] = label_text
            filename = sanitize_filename(label_text) + '.stl'

        if not filename:
            filename = sanitize_filename(label_text) + '.stl'

        export_path = os.path.join(output_dir, filename)

        # Merge batch kwargs
        merged_kwargs = {**kwargs, **label_kwargs}

        try:
            label = create_label(export_path=export_path, **merged_kwargs)
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

    # Example 1: Single-line labels (simple batch)
    labels = [
        "EMS Shirts",
        "EMS Pants",
        "Work Shirts",
        "Work Pants",
        "Cold Weather",
    ]

    # Output directory
    output_dir = "/tmp/labels"

    # Create all labels with default settings
    # created_labels = create_label_batch(labels, output_dir)

    # Example 2: Multi-line labels (manual creation)
    # Create a label with multiple lines
    label1 = create_label(
        line1="Zone 1",
        line2="Heat Only",
        line3="Main Floor",
        export_path=f"{output_dir}/Zone_1.stl"
    )

    label2 = create_label(
        line1="Hot Water",
        line2="120°F",
        export_path=f"{output_dir}/Hot_Water.stl",
        base_width=60.0,    # Wider for longer text
        text_size=3.5       # Slightly larger text
    )

    # Example 3: Single label with custom settings
    label3 = create_label(
        line1="Boiler",
        line2="Room #3",
        export_path=f"{output_dir}/Boiler_Room_3.stl",
        base_width=60.0,           # Wider label
        base_height=15.0,          # Taller label
        text_size=4.0,             # Larger text
        hole_diameter=3.0,         # Bigger holes
        hole_inset=4.0             # Further from edges
    )

    print("\n✓ Script completed successfully!")

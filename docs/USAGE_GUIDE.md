# Blender Printable Labels - Usage Guide

A reusable Blender script for creating 3D printable closet labels with mounting holes.

## 📥 Files

- `label_generator.py` - The main reusable script
- This guide - Instructions and examples

---

## 🚀 Quick Start

### Method 1: Run in Blender Text Editor

1. Open Blender
2. Switch to "Scripting" workspace (top menu)
3. Click "Open" and select `label_generator.py`
4. Modify the labels list at the bottom of the script
5. Click "Run Script" or press `Alt + P`

### Method 2: Run from Blender Console

```python
# Import the module
exec(open("/path/to/label_generator.py").read())

# Create a single label
label = create_label(line1="Kitchen", export_path="/path/to/Kitchen.stl")

# Create multiple labels
labels = [("Pantry", "Pantry.stl"), ("Garage", "Garage.stl")]
create_label_batch(labels, "/path/to/output/")
```

---

## 📖 Function Reference

### `create_label()`

Create a single label with full customization.

**Basic Usage:**
```python
label = create_label(line1="My Label", export_path="/path/to/output.stl")
```

**With Custom Settings:**
```python
label = create_label(
    label_text="Custom Label",
    export_path="/path/to/output.stl",
    base_width=60.0,           # Width in mm (default: 50.0)
    base_height=15.0,          # Height in mm (default: 12.5)
    base_thickness=2.0,        # Thickness in mm (default: 1.25)
    text_size=4.0,             # Text size in mm (default: 3.0)
    text_extrude=0.75,         # Text depth in mm (default: 0.5)
    hole_diameter=3.0,         # Hole diameter in mm (default: 2.5)
    hole_inset=4.0,            # Inset from edges in mm (default: 3.0)
    mirror_text=True,          # Mirror text (default: True)
    apply_booleans=True,       # Apply boolean ops (default: True)
    delete_cylinders=True      # Delete hole cylinders (default: True)
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label_text` | str | *required* | Text to display on the label |
| `export_path` | str | None | Full path to export STL (None = don't export) |
| `base_width` | float | 50.0 | Width of label in mm |
| `base_height` | float | 12.5 | Height of label in mm |
| `base_thickness` | float | 1.25 | Thickness of base in mm |
| `text_size` | float | 3.0 | Text size in mm |
| `text_extrude` | float | 0.5 | Text extrusion depth in mm |
| `hole_diameter` | float | 2.5 | Diameter of mounting holes in mm |
| `hole_inset` | float | 3.0 | Distance from edges to hole centers in mm |
| `mirror_text` | bool | True | Mirror text on Y-axis for readability |
| `apply_booleans` | bool | True | Apply boolean modifiers |
| `delete_cylinders` | bool | True | Delete cylinder objects after boolean |

### `create_label_batch()`

Create multiple labels at once.

**Usage:**
```python
labels = [
    ("Kitchen", "Kitchen.stl"),
    ("Bathroom", "Bathroom.stl"),
    "Living Room"  # filename auto-generated as Living_Room.stl
]

create_label_batch(labels, "/path/to/output/")
```

**With Custom Settings for All Labels:**
```python
create_label_batch(
    labels,
    "/path/to/output/",
    base_width=60.0,      # All labels will be 60mm wide
    text_size=4.0         # All labels will have 4mm text
)
```

### `clear_existing_labels()`

Delete all existing label objects from the scene.

**Usage:**
```python
clear_existing_labels()
```

---

## 💡 Example Use Cases

### Example 1: Standard Closet Labels

```python
labels = [
    "Shirts",
    "Pants", 
    "Dresses",
    "Jackets"
]

create_label_batch(labels, "/home/user/closet_labels/")
```

### Example 2: Kitchen Organization

```python
kitchen_labels = [
    ("Spices", "kitchen_spices.stl"),
    ("Baking", "kitchen_baking.stl"),
    ("Canned Goods", "kitchen_canned.stl"),
    ("Snacks", "kitchen_snacks.stl")
]

create_label_batch(kitchen_labels, "/home/user/kitchen/")
```

### Example 3: Large Labels for Garage

```python
garage_labels = ["Tools", "Hardware", "Paint", "Garden"]

create_label_batch(
    garage_labels,
    "/home/user/garage/",
    base_width=75.0,        # Larger labels
    base_height=20.0,
    text_size=5.0,
    hole_diameter=4.0       # Bigger mounting holes
)
```

### Example 4: Small Labels for Drawers

```python
drawer_labels = ["Batteries", "Cables", "Screws", "Tape"]

create_label_batch(
    drawer_labels,
    "/home/user/drawers/",
    base_width=40.0,        # Smaller labels
    base_height=10.0,
    text_size=2.5,
    hole_diameter=2.0
)
```

### Example 5: Create Without Exporting

Useful if you want to manually adjust labels before exporting:

```python
# Create labels in scene without exporting
labels = create_label(line1="Test Label", export_path=None)

# Manually adjust in Blender, then export when ready
```

### Example 6: Custom Mounting Pattern

```python
# Create label but don't apply booleans yet
label = create_label(
    "Custom", 
    export_path=None,
    apply_booleans=False,
    delete_cylinders=False
)

# Now you can manually adjust cylinder positions in Blender
# Then apply booleans manually when satisfied
```

---

## 🎨 Customization Tips

### Text Positioning

The text is automatically centered and positioned above the base. The Y-axis mirroring makes it readable from both sides of the label.

### Hole Positioning

Holes are automatically positioned based on:
- `hole_inset`: Distance from each edge
- Formula: 
  - X: `±(base_width/2 - hole_inset)`
  - Y: `±(base_height/2 - hole_inset)`

### Recommended Dimensions

**Standard Closet Labels:**
- Width: 50-75mm
- Height: 12.5-20mm
- Thickness: 1.25-2.0mm
- Hole diameter: 2.5-3.5mm

**Small Drawer Labels:**
- Width: 30-40mm
- Height: 8-10mm
- Thickness: 1.0-1.5mm
- Hole diameter: 2.0-2.5mm

**Large Garage/Storage Labels:**
- Width: 75-100mm
- Height: 20-30mm
- Thickness: 2.0-3.0mm
- Hole diameter: 3.5-5.0mm

---

## 🖨️ 3D Printing Tips

**Recommended Settings:**
- Layer Height: 0.15-0.2mm
- Infill: 20-30%
- Supports: None needed
- Orientation: Print flat as created
- Material: PLA, PETG, or ABS

**Best Practices:**
- Print with contrasting colors for better text visibility
- Use a textured build plate for better first layer adhesion
- Consider printing text in different color (pause print to swap filament)

---

## 🔧 Troubleshooting

**Problem: Text is backwards**
- Solution: Ensure `mirror_text=True` is set

**Problem: Holes not appearing**
- Solution: Make sure `apply_booleans=True`

**Problem: Cylinders still in scene**
- Solution: Set `delete_cylinders=True`

**Problem: Label too large/small**
- Solution: Adjust `base_width` and `base_height` parameters

**Problem: Text doesn't fit**
- Solution: Reduce `text_size` or increase `base_width`

**Problem: Export fails**
- Solution: Ensure output directory exists and you have write permissions

---

## 📝 Notes

- All dimensions are in millimeters
- The script uses binary STL format for maximum compatibility
- Labels are created at the origin (0,0,0) with Z at half thickness
- Mesh is automatically made manifold and watertight
- No supports needed for printing

---

## 🎯 Default Specifications

These are the tested and verified defaults used for the closet labels:

```python
base_width = 50.0 mm
base_height = 12.5 mm
base_thickness = 1.25 mm
text_size = 3.0 mm
text_extrude = 0.5 mm
hole_diameter = 2.5 mm
hole_inset = 3.0 mm
```

**Hole Positions (for default 50mm x 12.5mm label):**
- Top-left: (-22, 3.25, 1.25)
- Top-right: (22, 3.25, 1.25)
- Bottom-left: (-22, -3.25, 1.25)
- Bottom-right: (22, -3.25, 1.25)

---

## 🚀 Advanced Usage

### Integrate into Addon

To integrate this into a Blender addon:

```python
from . import label_generator as lg

class OBJECT_OT_create_label(bpy.types.Operator):
    bl_idname = "object.create_label"
    bl_label = "Create Closet Label"
    
    def execute(self, context):
        clg.create_label(line1="Test", export_path="/tmp/test.stl")
        return {'FINISHED'}
```

### Batch Processing with CSV

```python
import csv

# Read labels from CSV file
with open('labels.csv', 'r') as f:
    reader = csv.reader(f)
    labels = [(row[0], f"{row[0]}.stl") for row in reader]

create_label_batch(labels, "/output/path/")
```

---

Happy labeling! 🏷️

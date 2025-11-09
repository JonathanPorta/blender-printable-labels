# Blender Printable Labels Addon - Installation & Usage

## 📦 Installation

### Step 1: Install the Addon

1. **Save the addon file:**
   - Download `blender_printable_labels.py`

2. **Open Blender:**
   - Go to `Edit > Preferences` (or `Blender > Preferences` on Mac)

3. **Install addon:**
   - Click the `Add-ons` tab
   - Click `Install...` button at the top
   - Navigate to and select `blender_printable_labels.py`
   - Click `Install Add-on`

4. **Enable the addon:**
   - Search for "Blender Printable" or "Label" in the addons list
   - Check the checkbox next to "Add Mesh: Blender Printable Labels"
   - The addon is now active!

### Step 2: Access the UI

1. **Open 3D Viewport** (default view)
2. **Press `N`** to open the sidebar (if not already visible)
3. **Click "Label Maker" tab** in the sidebar
4. You'll see three panels:
   - **Label Generator** - Create single labels
   - **Batch Creation** - Create multiple labels at once
   - **Utilities** - Scene management tools

---

## 🎨 UI Overview

### Label Maker Sidebar Tab

The addon adds a "Label Maker" tab to the 3D Viewport sidebar with three collapsible panels:

```
┌─────────────────────────────┐
│ 🏷️  LABEL MAKER            │
├─────────────────────────────┤
│ ▼ Label Generator           │
│   ┌─────────────────────┐   │
│   │ Label Text          │   │
│   │ [My Label_______]   │   │
│   └─────────────────────┘   │
│                             │
│   Size Preset               │
│   [Closet Standard ▼]       │
│                             │
│   Dimensions                │
│   Width:      50.00 mm      │
│   Height:     12.50 mm      │
│   Thickness:   1.25 mm      │
│                             │
│   Text Settings             │
│   Text Size:   3.00 mm      │
│   Text Depth:  0.50 mm      │
│   ☑ Mirror Text             │
│                             │
│   Mounting Holes            │
│   Hole Diameter: 2.50 mm    │
│   Hole Inset:    3.00 mm    │
│                             │
│   Options                   │
│   ☑ Apply Booleans          │
│   ☑ Delete Cylinders        │
│                             │
│   Export                    │
│   ☑ Auto Export STL         │
│   Path: //labels/           │
│                             │
│   [    Create Label    ]    │
│                             │
├─────────────────────────────┤
│ ▶ Batch Creation            │
├─────────────────────────────┤
│ ▶ Utilities                 │
└─────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Create Your First Label

1. **Open the sidebar** (Press `N`)
2. **Click "Label Maker" tab**
3. **Enter your text** in the "Label Text" field
4. **Click "Create Label"** button
5. Done! Your label appears at the origin (0,0,0)

### Create Multiple Labels (Batch Mode)

1. **Expand "Batch Creation" panel**
2. **Click "Load Closet Presets"** to load 10 common labels
   - OR click `+` to add custom labels one by one
3. **Edit any label text** by selecting it in the list
4. **Click "Create Batch"** button
5. All enabled labels are created!

---

## 🎛️ UI Components Reference

### Main Panel: Label Generator

#### Label Text
- **Type:** Text input field
- **What it does:** The text that will appear on your label
- **Example:** "Kitchen", "Pantry", "Tools"

#### Size Preset Dropdown
Quick size presets for common use cases:

| Preset | Width | Height | Text Size | Use Case |
|--------|-------|--------|-----------|----------|
| **Closet Standard** | 50mm | 12.5mm | 3mm | Standard closet organization |
| **Drawer Small** | 40mm | 10mm | 2.5mm | Small drawers, bins |
| **Garage Large** | 75mm | 20mm | 5mm | Large storage, garage |
| **Wide** | 100mm | 15mm | 4mm | Long text labels |
| **Custom** | — | — | — | Manual dimensions |

#### Dimensions Section
- **Width:** Label width in millimeters (10-200mm)
- **Height:** Label height in millimeters (5-100mm)
- **Thickness:** Base thickness in millimeters (0.5-10mm)

*All dimensions auto-adjust when you select a preset!*

#### Text Settings Section
- **Text Size:** Height of text in millimeters (0.5-20mm)
- **Text Depth:** How much text protrudes from base (0.1-5mm)
- **☑ Mirror Text:** When checked, text is readable from both sides

#### Mounting Holes Section
- **Hole Diameter:** Diameter of mounting holes (1-20mm)
  - *Tip: Common M3 screw = 3mm, #6 screw ≈ 3.5mm*
- **Hole Inset:** Distance from edges to hole centers (1-20mm)
  - *Tip: More inset = stronger edges, less likely to break*

#### Options Section
- **☑ Apply Booleans:** Applies hole cutting operation
  - *Uncheck to manually adjust holes before applying*
- **☑ Delete Cylinders:** Removes cylinder objects after cutting
  - *Uncheck to keep cylinders for reference*

#### Export Section
- **☑ Auto Export STL:** Automatically saves STL file when creating
- **Export Path:** Where to save STL files
  - *`//` means relative to your .blend file location*
  - *Example: `//labels/` creates a "labels" folder next to your .blend*

---

### Batch Creation Panel

#### Preset Button
- **Load Closet Presets:** Instantly loads these 10 labels:
  1. EMS Shirts
  2. EMS Pants
  3. Work Shirts
  4. Work Pants
  5. Cold Weather
  6. Golf Shirts
  7. Dress Shirts
  8. Regular T Shirts
  9. Regular Pants
  10. Dresses

#### Label List
- Shows all labels in your batch
- Click a label to edit it
- Checkboxes show which labels are enabled

#### List Controls
- **`+` button:** Add a new empty label
- **`-` button:** Remove selected label

#### Selected Label Editor
- **Text:** Edit the text for selected label
- **☑ Include in Batch:** Toggle this label on/off

#### Create Batch Button
- Creates all enabled labels at once
- Uses the settings from the main "Label Generator" panel

---

### Utilities Panel

#### Scene Management
- **Clear All Labels:** Deletes all label objects from scene
  - *Useful when starting fresh or after testing*

#### Info Display
- Shows how many labels are currently in the scene
- *Example: "Labels in scene: 10"*

---

## 💡 Workflow Examples

### Example 1: Quick Single Label

```
1. Press N → Label Maker tab
2. Type "Kitchen" in Label Text
3. Click "Create Label"
✓ Done in 3 clicks!
```

### Example 2: Closet Organization Set

```
1. Batch Creation → Load Closet Presets
2. Review/edit any labels you want
3. Enable "Auto Export STL"
4. Set export path to "//closet_labels/"
5. Click "Create Batch"
✓ 10 labels created and exported!
```

### Example 3: Custom Garage Labels

```
1. Select "Garage Large" preset
2. Batch Creation panel:
   - Click + to add label
   - Type "Power Tools"
   - Click + again
   - Type "Hand Tools"
   - Click + again
   - Type "Fasteners"
3. Adjust hole diameter to 4mm (larger screws)
4. Click "Create Batch"
✓ 3 custom garage labels!
```

### Example 4: Drawer Organization

```
1. Select "Drawer Small" preset
2. Change dimensions if needed
3. Create labels one at a time:
   - "Batteries"
   - "Cables"
   - "Tape"
   - "Markers"
4. Use Utilities → Clear All Labels between tests
✓ Perfect fit for small drawers!
```

---

## ⌨️ Keyboard Shortcuts

While in 3D Viewport:
- **`N`** - Toggle sidebar (show/hide Label Maker)
- **`Alt + P`** - Run script (if in Text Editor)

No custom shortcuts are registered by the addon to avoid conflicts.

---

## 🎯 Tips & Tricks

### Best Practices

1. **Save your .blend file first**
   - Export paths with `//` are relative to .blend file location
   - Makes it easy to keep STLs organized

2. **Test with one label first**
   - Adjust settings to your liking
   - Then use batch creation for many labels

3. **Use presets as starting points**
   - Select a preset close to what you want
   - Then fine-tune individual values

4. **Enable Auto Export for batch jobs**
   - Saves time when creating many labels
   - Automatically names files based on label text

5. **Keep cylinders for experimentation**
   - Uncheck "Delete Cylinders"
   - Manually adjust hole positions
   - Apply booleans when satisfied

### Size Recommendations

**For readability:**
- Text should be at least 2mm tall
- Text depth around 0.5mm is good for most cases
- Wider labels = more room for text

**For strength:**
- Minimum thickness: 1mm (but 1.25mm+ recommended)
- Hole inset: At least 2.5-3mm from edges
- Larger holes need more inset

**For printing:**
- Labels print best flat (as created)
- No supports needed
- 0.2mm layer height works great

### Common Dimensions

**Standard business card size:**
```
Width: 85mm
Height: 55mm
(but scale down to 50-60mm width for practical labels)
```

**Credit card size:**
```
Width: 85.6mm
Height: 53.98mm
(again, scale to practical size)
```

**Custom calculations:**
```
Text width ≈ Text Size × Number of Characters × 0.6
(rough estimate, actual depends on font)
```

---

## 🔧 Troubleshooting

### "Label Maker tab doesn't appear"
- Make sure addon is enabled in Preferences
- Press `N` to show sidebar
- Restart Blender if needed

### "Text doesn't fit on label"
- Increase `Width` value
- Decrease `Text Size` value
- Use shorter text

### "Holes aren't appearing"
- Make sure `Apply Booleans` is checked
- Check that `Hole Inset` isn't larger than half the label size

### "Export path error"
- Make sure you've saved your .blend file first (for `//` paths)
- Or use absolute path like `/home/user/labels/`
- Check you have write permissions to the folder

### "Labels are too small/large in viewport"
- All dimensions are in millimeters
- Blender's grid squares are 1 Blender unit = 1 meter by default
- Labels will print at correct size regardless of viewport appearance

### "Batch creation creates labels in same spot"
- This is normal! They stack on top of each other
- Each is a separate object with different text
- Select individual labels in Outliner to work with them
- Or export them and they'll be separate STL files

---

## 📊 UI Advantages vs. Script

### Why UI is Better:

✅ **Instant feedback** - See parameter changes immediately
✅ **No coding needed** - Just fill in fields and click
✅ **Visual organization** - Everything grouped logically
✅ **Presets** - One click to common sizes
✅ **Batch list** - Visual list of all labels to create
✅ **Persistent settings** - Values saved with .blend file
✅ **Discoverable** - Easy to explore options
✅ **Undo support** - Built-in with `Ctrl+Z`

### Script Still Useful For:

- Automation from command line
- Integration with other Python scripts
- Advanced customization beyond UI options
- Programmatic generation from databases/CSV

---

## 🎓 Learning More

### Blender UI Concepts

The addon uses standard Blender UI patterns:

- **Properties:** Values stored in scene (persist with file)
- **Operators:** Actions that can be undone
- **Panels:** Collapsible UI sections
- **Presets:** Predefined value combinations

### Customizing the Addon

Want to modify the addon? Key sections:

- **Line 22:** `bl_info` - Addon metadata
- **Line 53:** `LabelGeneratorProperties` - All the settings
- **Line 230:** Operators - The "do something" actions
- **Line 407:** Panels - The UI layout

---

## ✨ Summary

The addon gives you a full UI with:

- **13 adjustable parameters** with appropriate widgets
- **5 size presets** for one-click sizing
- **Batch creation** with visual list
- **Auto export** to STL
- **Scene utilities** for cleanup
- **All without writing a single line of code!**

Just install, open sidebar, and start creating labels! 🚀

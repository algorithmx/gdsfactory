# Cross-Section Export

This module provides functionality to generate vertical cross-section images from GDS files or Components.

## Overview

The cross-section export transforms 2D GDS layouts into vertical cross-sectional views by:
1. Reading the GDS file or Component
2. Extruding 2D polygons to 3D using LayerStack thickness/zmin data
3. Slicing the 3D geometry with a vertical plane
4. Rendering the intersection as a PNG image

## API

### Main Function

```python
from gdsfactory.export import to_cross_section

def to_cross_section(
    component: Component | str | Path,
    plane_position: float,
    plane_direction: Literal["x", "y"],
    layer_stack: LayerStack | None = None,
    layer_views: LayerViews | str | Path | None = None,
    exclude_layers: LayerSpecs | None = None,
    filename: str | Path | None = None,
    show: bool = False,
    dpi: int = 150,
    **kwargs: Any,
) -> Figure | None:
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `component` | `Component` \| `str` \| `Path` | Component object or path to GDS file |
| `plane_position` | `float` | Coordinate of slicing plane in microns |
| `plane_direction` | `"x"` \| `"y"` | Direction perpendicular to slicing plane. `"x"` = slice perpendicular to x-axis (show y-z plane), `"y"` = slice perpendicular to y-axis (show x-z plane) |
| `layer_stack` | `LayerStack` \| `None` | Contains thickness and zmin for each layer. Defaults to active PDK.layer_stack |
| `layer_views` | `LayerViews` \| `str` \| `Path` \| `None` | Layer colors from KLayout Layer Properties file. Defaults to active PDK.layer_views |
| `exclude_layers` | `LayerSpecs` \| `None` | List of layer indices to exclude |
| `filename` | `str` \| `Path` \| `None` | Output PNG filename. If None, returns figure without saving |
| `show` | `bool` | If True, display the plot interactively |
| `dpi` | `int` | Resolution for output image (default: 150) |
| `**kwargs` | `Any` | Additional matplotlib arguments |

### Returns

- `matplotlib.figure.Figure` if `filename` is `None`
- `None` if `filename` is provided (saves to file)

### Raises

- `ValueError`: If no layers intersect the slicing plane
- `ValueError`: If all layers are excluded or not found

## Usage Examples

### Basic Usage

```python
import gdsfactory as gf

# Create a simple component
c = gf.components.rectangle(size=(10, 10), layer=(2, 0))

# Generate cross-section (displays as figure)
fig = gf.export.to_cross_section(
    c,
    plane_position=5.0,  # Slice at x = 5 µm
    plane_direction="x"   # Show y-z plane
)
```

### Save to File

```python
# Save cross-section to PNG file
gf.export.to_cross_section(
    "design.gds",
    plane_position=5.0,
    plane_direction="y",
    filename="cross_section.png"
)
```

### Custom LayerStack

```python
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer

# Define custom layer stack
layer_stack = LayerStack(
    layers=dict(
        substrate=LayerLevel(
            layer=LogicalLayer(layer=(1, 0)),
            thickness=2.0,
            zmin=-2.0,
            material="si",
            mesh_order=99,
        ),
        core=LayerLevel(
            layer=LogicalLayer(layer=(2, 0)),
            thickness=0.22,
            zmin=0.0,
            material="si",
            mesh_order=2,
        ),
    )
)

# Use custom LayerStack
fig = gf.export.to_cross_section(
    c,
    plane_position=5.0,
    plane_direction="x",
    layer_stack=layer_stack,
)
```

### Both Directions

```python
# X-direction cross-section (shows y-z plane at x = 5 µm)
fig_x = gf.export.to_cross_section(
    c, plane_position=5.0, plane_direction="x"
)

# Y-direction cross-section (shows x-z plane at y = 5 µm)
fig_y = gf.export.to_cross_section(
    c, plane_position=5.0, plane_direction="y"
)
```

### Excluding Layers

```python
# Exclude specific layers from the cross-section
fig = gf.export.to_cross_section(
    c,
    plane_position=5.0,
    plane_direction="x",
    exclude_layers=[(3, 0), (4, 0)],  # Exclude layers 3/0 and 4/0
)
```

## Implementation Architecture

### Algorithm Overview

```
GDS File/Component → LayerStack Extrusion → 3D Meshes → Plane Slice → 2D Profile → PNG Image
                       (thickness/zmin)      (trimesh)    (mesh_plane)   (matplotlib)
```

### Components

#### 1. `_get_layer_meshes()`

Creates 3D meshes for each layer in the LayerStack by:
- Getting polygons from the component (with derived layers applied)
- Extruding each 2D polygon vertically using `trimesh.creation.extrude_polygon()`
- Positioning meshes at correct z-height using `level.zmin`
- Applying layer colors from LayerViews
- Returning dict mapping layer_name → (LayerLevel, mesh)

#### 2. `_slice_mesh_with_plane()`

Slices each 3D mesh with a vertical plane:
- Uses `trimesh.intersections.mesh_plane()` for intersection
- Plane definition:
  - For `plane_direction='x'`: normal=[1, 0, 0], origin=[plane_position, 0, 0]
  - For `plane_direction='y'`: normal=[0, 1, 0], origin=[0, plane_position, 0]
- Returns list of line segments (numpy arrays) at the intersection

#### 3. `_lines_to_cross_section_profile()`

Converts intersection line segments to 2D profiles:
- Projects 3D line segments to 2D (horizontal vs. vertical)
- For x-plane: extracts (y, z) coordinates
- For y-plane: extracts (x, z) coordinates
- Attaches metadata (material, color, zmin, zmax, layer_name)

#### 4. `_render_cross_section()`

Renders profiles to matplotlib figure:
- Creates convex hull from intersection points
- Fills polygons with layer colors
- Adds material legend
- Sets labels and aspect ratio
- Saves to file or displays interactively

### Layer/Material Tracking Strategy

Layer metadata is preserved throughout the pipeline:
1. Layer names from `LayerStack.layers.keys()`
2. Material from `LevelLevel.material`
3. Colors from `LayerViews.fill_color`
4. zmin/zmax from `LayerLevel.zmin` and `LayerLevel.thickness`

## Dependencies

All required libraries are already gdsfactory dependencies:

| Library | Version | Purpose |
|---------|---------|---------|
| `trimesh` | >=4.4.1 | 3D mesh operations and plane intersection |
| `shapely` | <3 | Polygon operations |
| `matplotlib` | <4 | PNG rendering and visualization |
| `numpy` | - | Array operations |
| `scipy` | - | Convex hull computation |

## Limitations

### Current Limitations

1. **Simplified Polygon Reconstruction**: Uses convex hull approximation for cross-section polygons. For complex geometries with holes or non-convex shapes, the reconstruction may not be exact.

2. **Vertical Sidewalls Only**: Does not account for `sidewall_angle` in LayerLevel. All extrusions are treated as vertical.

3. **Axis-Aligned Planes Only**: Only supports planes perpendicular to x or y axes. Arbitrary plane orientations are not supported.

4. **2D Output Only**: Outputs 2D PNG images. No 3D interactive visualization.

5. **Plane-Geometry Intersection**: May have numerical precision issues when the plane is exactly at mesh boundaries.

### Edge Cases Handled

- No layers at plane position → Raises `ValueError`
- Plane outside component bounds → Raises `ValueError`
- All layers excluded → Raises `ValueError`
- Multiple disconnected regions → Renders all regions
- Empty component → Raises `ValueError`

## Future Enhancements

Potential improvements for future versions:

### High Priority

1. **Accurate Polygon Reconstruction**: Implement proper polygon reconstruction from line segments using graph algorithms to handle holes and non-convex shapes.

2. **Sidewall Angle Support**: Incorporate `sidewall_angle` from LayerLevel for tapered extrusions.

3. **Multiple Cross-Sections**: Generate multiple cross-sections at different positions in a single call.

### Medium Priority

4. **Additional Output Formats**: Support SVG, PDF, or JSON output formats.

5. **Dimension Annotations**: Add automatic dimension labels for layer thicknesses and positions.

6. **Interactive Visualization**: Support for interactive 3D cross-section viewing.

### Low Priority

7. **Arbitrary Plane Orientation**: Support for planes at arbitrary angles.

8. **Measurement Tools**: Interactive tools to measure distances and angles in the cross-section.

9. **Material Properties Visualization**: Color-coding based on refractive index or other material properties.

## Files

- **Implementation**: `gdsfactory/export/to_cross_section.py`
- **Tests**: `tests/export/test_cross_section.py`
- **Export Index**: `gdsfactory/export/__init__.py`

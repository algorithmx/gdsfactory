# Change Log

## [NEW] GDS Cross-Section Export (`to_cross_section`)

### Overview
Implemented a new export function `to_cross_section()` that generates vertical cross-section images from GDS files or Components. This transforms 2D GDS layouts into vertical cross-sectional views for visualization and analysis.

### API
```python
from gdsfactory.export import to_cross_section

fig = to_cross_section(
    component,           # Component object or path to GDS file
    plane_position=5.0,  # Coordinate of slicing plane in microns
    plane_direction="x", # "x" = show y-z plane, "y" = show x-z plane
    layer_stack=None,    # Defaults to active PDK.layer_stack
    layer_views=None,    # Defaults to active PDK.layer_views
    exclude_layers=None, # Optional layers to exclude
    filename=None,       # If None, returns Figure; else saves to PNG
    show=False,          # Display interactively
    dpi=150,             # Output resolution
)
```

### Implementation Details
- **File**: `gdsfactory/export/to_cross_section.py` (~480 lines)
- **Docs**: `gdsfactory/export/README_cross_section.md`
- **Tests**: `tests/export/test_cross_section.py` (7 test cases)
- **Export**: Exposed via `gdsfactory.export.__init__.py`

### Algorithm Pipeline
```
GDS/Component ’ LayerStack Extrusion ’ 3D Meshes ’ Plane Slice ’ 2D Profile ’ PNG/Matplotlib
```

1. **`_get_layer_meshes()`**: Extrudes 2D polygons to 3D using LayerStack thickness/zmin
2. **`_slice_mesh_with_plane()`**: Intersects 3D meshes with vertical plane using `trimesh.intersections.mesh_plane()`
3. **`_lines_to_cross_section_profile()`**: Projects 3D intersection lines to 2D (x-z or y-z)
4. **`_render_cross_section()`**: Renders matplotlib figure with convex hull polygon reconstruction

### Key Features
- Supports both x and y direction cross-sections
- Custom LayerStack and LayerViews support
- Layer exclusion capability
- Returns matplotlib Figure or saves to PNG file
- Material/layer legend with colors from LayerViews
- Proper error handling for non-intersecting planes

### Dependencies (all existing)
- `trimesh` >=4.4.1 - 3D mesh operations
- `shapely` <3 - Polygon operations
- `matplotlib` <4 - PNG rendering
- `scipy` - Convex hull computation

### Current Limitations
- Uses convex hull approximation (may not handle holes/non-convex shapes accurately)
- Does not support `sidewall_angle` (vertical extrusions only)
- Axis-aligned planes only (perpendicular to x or y axes)
- 2D PNG output only (no 3D interactive visualization)

### Test Coverage
- Basic cross-section generation
- File saving
- Both x and y directions
- Error handling for non-intersecting planes
- Component vs GDS file input
- Layer exclusion
- Multiple layers in LayerStack

### Files Added/Modified
- **NEW**: `gdsfactory/export/to_cross_section.py`
- **NEW**: `gdsfactory/export/README_cross_section.md`
- **NEW**: `tests/export/test_cross_section.py`
- **MODIFIED**: `gdsfactory/export/__init__.py` (added `to_cross_section` export)

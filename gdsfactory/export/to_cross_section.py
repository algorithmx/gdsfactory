"""Cross-section export for GDS components.

Generates vertical cross-section images from GDS files by:
1. Reading GDS file and converting to Component
2. Extruding to 3D using LayerStack
3. Slicing with a vertical plane
4. Rendering the cross-section as PNG
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

import numpy as np
import shapely
import shapely.geometry
from matplotlib.figure import Figure
from trimesh.intersections import mesh_plane

from gdsfactory.read.import_gds import import_gds
from gdsfactory.typings import LayerSpecs, PathType

if TYPE_CHECKING:
    import trimesh

    from gdsfactory.component import Component
    from gdsfactory.technology import DerivedLayer, LayerLevel, LayerStack, LayerViews, LogicalLayer


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
    """Generate vertical cross-section image from GDS file or Component.

    Args:
        component: Component object or path to GDS file.
        plane_position: Coordinate of slicing plane in microns.
        plane_direction: Direction perpendicular to slicing plane ('x' or 'y').
            'x' = slice perpendicular to x-axis (show y-z plane)
            'y' = slice perpendicular to y-axis (show x-z plane)
        layer_stack: Contains thickness and zmin for each layer.
            Defaults to active PDK.layer_stack.
        layer_views: Layer colors from Klayout Layer Properties file.
            Defaults to active PDK.layer_views.
        exclude_layers: List of layer indices to exclude.
        filename: Output PNG filename. If None, returns figure without saving.
        show: If True, display the plot interactively.
        dpi: Resolution for output image.
        **kwargs: Additional arguments passed to matplotlib.

    Returns:
        matplotlib Figure if filename is None, otherwise None.

    Raises:
        ValueError: If no layers intersect the slicing plane.
    """
    # Import dependencies locally following gdsfactory pattern
    from gdsfactory.pdk import get_layer, get_layer_stack, get_layer_views

    # Get defaults from active PDK
    layer_stack = layer_stack or get_layer_stack()
    layer_views = layer_views or get_layer_views()

    if isinstance(layer_views, str | Path):
        from gdsfactory.technology import LayerViews

        layer_views = LayerViews(layer_views)

    # Import GDS file if path is provided, otherwise use component directly
    if isinstance(component, str | Path):
        component = import_gds(component)

    # Convert to 3D meshes (similar to to_3d but preserve layer names)
    layer_meshes = _get_layer_meshes(
        component, layer_stack, layer_views, exclude_layers
    )

    if not layer_meshes:
        raise ValueError(
            f"No layers found. Check that layer_stack contains layers "
            f"that exist in the component and are not all excluded."
        )

    # Collect cross-section profiles from each layer
    profiles = []

    for layer_name, (level, mesh) in layer_meshes.items():
        # Slice mesh with plane
        lines = _slice_mesh_with_plane(mesh, plane_position, plane_direction)

        if lines is None or len(lines) == 0:
            # No intersection with this layer
            continue

        # Convert line segments to cross-section profile
        profile = _lines_to_cross_section_profile(
            lines, plane_direction, level, layer_views
        )

        if profile is not None:
            profiles.append(profile)

    if not profiles:
        raise ValueError(
            f"No layers found at plane_position={plane_position} "
            f"with plane_direction='{plane_direction}'. "
            f"Check that the plane intersects with the component."
        )

    # Render cross-section
    fig = _render_cross_section(
        profiles,
        plane_position,
        plane_direction,
        filename=filename,
        show=show,
        dpi=dpi,
        **kwargs,
    )

    return fig if filename is None else None


def _get_layer_meshes(
    component: Component,
    layer_stack: LayerStack,
    layer_views: LayerViews,
    exclude_layers: LayerSpecs | None = None,
) -> dict[str, tuple[Any, "trimesh.Trimesh"]]:
    """Create 3D meshes for each layer in the LayerStack.

    Returns dict mapping layer_name to (LayerLevel, mesh) tuples.

    This is similar to to_3d() but preserves layer names and returns
    the meshes directly rather than a Scene object.
    """
    from gdsfactory.pdk import get_layer

    try:
        from trimesh.creation import extrude_polygon
    except ImportError:
        print("you need to `pip install trimesh`")
        raise

    from trimesh.visual import ColorVisuals

    layer_meshes = {}
    exclude_layers = exclude_layers or ()
    exclude_layer_indices = [get_layer(layer) for layer in exclude_layers]

    # Get component with derived layers applied
    component_with_booleans = layer_stack.get_component_with_derived_layers(component)
    polygons_per_layer = component_with_booleans.get_polygons_points(merge=True)

    for level in layer_stack.layers.values():
        layer = level.layer

        # Get layer tuple
        from gdsfactory.technology import DerivedLayer, LogicalLayer

        if isinstance(layer, LogicalLayer):
            layer_tuple = cast(
                "tuple[int, int]",
                tuple(layer.layer) if isinstance(layer.layer, tuple) else tuple(layer.layer),
            )
        elif isinstance(layer, DerivedLayer):
            assert level.derived_layer is not None
            layer_tuple = cast(
                "tuple[int, int]",
                tuple(level.derived_layer.layer)
                if isinstance(level.derived_layer.layer, tuple)
                else tuple(level.derived_layer.layer),
            )
        else:
            continue

        layer_index = int(get_layer(layer_tuple))

        if layer_index in exclude_layer_indices:
            continue

        if layer_index not in polygons_per_layer:
            continue

        zmin = level.zmin
        if zmin is None:
            continue

        layer_view = layer_views.get_from_tuple(layer_tuple)
        if layer_view is None or not layer_view.visible:
            continue

        assert layer_view.fill_color is not None
        color_rgb = [c / 255 for c in layer_view.fill_color.as_rgb_tuple(alpha=False)]

        # Create mesh for each polygon
        polygons = polygons_per_layer[layer_index]
        height = level.thickness

        meshes = []
        for polygon in polygons:
            p = shapely.geometry.Polygon(polygon)
            mesh = extrude_polygon(p, height=height)
            mesh.apply_translation((0, 0, zmin))
            if isinstance(mesh.visual, ColorVisuals):
                mesh.visual.face_colors = (*color_rgb, 0.5)
            meshes.append(mesh)

        if meshes:
            # Combine all meshes for this layer
            if len(meshes) == 1:
                combined_mesh = meshes[0]
            else:
                import trimesh

                combined_mesh = trimesh.util.concatenate(meshes)

            layer_name = level.name or f"layer_{layer_tuple[0]}_{layer_tuple[1]}"
            layer_meshes[layer_name] = (level, combined_mesh)

    return layer_meshes


def _slice_mesh_with_plane(
    mesh: "trimesh.Trimesh",
    plane_position: float,
    plane_direction: Literal["x", "y"],
) -> list[np.ndarray] | None:
    """Slice mesh with plane and return intersection line segments.

    Args:
        mesh: Trimesh mesh to slice.
        plane_position: Position of slicing plane in microns.
        plane_direction: Direction perpendicular to slicing plane.

    Returns:
        List of (N, 2, 3) numpy arrays representing line segments in 3D,
        or None if no intersection.
    """
    # Define plane
    normal = np.array([1.0, 0.0, 0.0]) if plane_direction == "x" else np.array([0.0, 1.0, 0.0])
    origin = np.array([plane_position, 0.0, 0.0]) if plane_direction == "x" else np.array([0.0, plane_position, 0.0])

    # Compute intersection
    # mesh_plane returns a (M, 2, 3) array of line segments
    # or an empty array if no intersection
    try:
        lines = mesh_plane(mesh, normal, origin)
        if lines is not None and len(lines) > 0:
            # Convert to list of numpy arrays, one per line segment
            return [np.array(line) for line in lines]
        return None
    except Exception:
        # No intersection or numerical error
        return None


def _lines_to_cross_section_profile(
    lines: list[np.ndarray],
    plane_direction: Literal["x", "y"],
    level: "LayerLevel",
    layer_views: LayerViews,
) -> dict[str, Any] | None:
    """Convert intersection line segments to cross-section profile.

    Args:
        lines: List of (N, 2, 3) arrays representing line segments.
        plane_direction: Direction perpendicular to slicing plane.
        level: LayerLevel from LayerStack.
        layer_views: LayerViews for color information.

    Returns:
        Dictionary with cross-section profile data including:
        - 'coords': (M, 2) array of (horizontal, vertical) coordinates
        - 'material': Material name
        - 'zmin': Minimum z position
        - 'zmax': Maximum z position
        - 'color': RGB color tuple
        - 'layer_name': Layer name
    """
    if not lines or len(lines) == 0:
        return None

    # Project 3D line segments to 2D
    # For x-plane: extract (y, z) coordinates
    # For y-plane: extract (x, z) coordinates
    horizontal_idx = 1 if plane_direction == "x" else 0
    vertical_idx = 2  # z is always index 2

    # Collect all points from line segments
    points_2d = []
    for line in lines:
        if line.shape[0] >= 2:
            # Extract endpoints
            pt1 = line[0]
            pt2 = line[1]
            points_2d.append([pt1[horizontal_idx], pt1[vertical_idx]])
            points_2d.append([pt2[horizontal_idx], pt2[vertical_idx]])

    if not points_2d:
        return None

    # Convert to numpy array
    coords = np.array(points_2d)

    # Get material information
    material = level.material or "unknown"

    # Get z-range
    zmin = level.zmin
    zmax = level.zmin + level.thickness

    # Get color from LayerViews
    from gdsfactory.technology import LogicalLayer, DerivedLayer

    if isinstance(level.layer, LogicalLayer):
        layer_tuple = (
            tuple(level.layer.layer) if isinstance(level.layer.layer, tuple) else tuple(level.layer.layer)
        )
    elif isinstance(level.layer, DerivedLayer) and level.derived_layer:
        layer_tuple = (
            tuple(level.derived_layer.layer) if isinstance(level.derived_layer.layer, tuple) else tuple(level.derived_layer.layer)
        )
    else:
        layer_tuple = (0, 0)

    try:
        layer_view = layer_views.get_from_tuple(layer_tuple)
        if layer_view and layer_view.fill_color:
            color = tuple(c / 255.0 for c in layer_view.fill_color.as_rgb_tuple(alpha=False))
        else:
            color = (0.5, 0.5, 0.5)  # Default gray
    except Exception:
        color = (0.5, 0.5, 0.5)  # Default gray

    return {
        "coords": coords,
        "material": material,
        "zmin": zmin,
        "zmax": zmax,
        "color": color,
        "layer_name": level.name or "unknown",
    }


def _render_cross_section(
    profiles: list[dict[str, Any]],
    plane_position: float,
    plane_direction: Literal["x", "y"],
    filename: str | Path | None = None,
    show: bool = False,
    dpi: int = 150,
    **kwargs: Any,
) -> Figure:
    """Render cross-section profiles to matplotlib figure.

    Args:
        profiles: List of cross-section profile dictionaries.
        plane_position: Position of slicing plane (for title).
        plane_direction: Direction of slicing plane (for labels).
        filename: Output PNG filename.
        show: If True, display the plot interactively.
        dpi: Resolution for output image.
        **kwargs: Additional matplotlib arguments.

    Returns:
        matplotlib Figure object.
    """
    import matplotlib.pyplot as plt
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Polygon

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6), dpi=dpi)

    # Collect materials for legend (deduplicate)
    seen_materials = set()
    legend_handles = []
    legend_labels = []

    # Render each profile
    for profile in profiles:
        coords = profile["coords"]
        color = profile["color"]
        material = profile["material"]
        layer_name = profile["layer_name"]

        # Create convex hull from points to get polygon shape
        # This is a simplification - for complex cross-sections,
        # we would need to properly reconstruct polygons from line segments
        try:
            from scipy.spatial import ConvexHull

            # Remove duplicate points
            unique_coords = np.unique(coords, axis=0)

            if len(unique_coords) >= 3:
                # Compute convex hull
                hull = ConvexHull(unique_coords)
                hull_coords = unique_coords[hull.vertices]

                # Create polygon patch
                poly_patch = Polygon(
                    hull_coords,
                    closed=True,
                    facecolor=color,
                    edgecolor="black",
                    linewidth=0.5,
                    alpha=0.8,
                    label=f"{material} ({layer_name})",
                )
                ax.add_patch(poly_patch)

                # Add to legend if not seen
                label_key = f"{material}_{layer_name}"
                if label_key not in seen_materials:
                    seen_materials.add(label_key)
                    legend_labels.append(f"{material} ({layer_name})")
                    legend_handles.append(poly_patch)
        except Exception:
            # Fallback: scatter plot of points
            ax.scatter(
                coords[:, 0],
                coords[:, 1],
                c=[color],
                s=10,
                alpha=0.6,
                label=f"{material} ({layer_name})",
            )

    # Set labels
    xlabel = "Y (µm)" if plane_direction == "x" else "X (µm)"
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Z (µm)")
    ax.set_title(f"Cross-Section at {plane_direction.upper()} = {plane_position:.3f} µm")

    # Set aspect ratio
    ax.set_aspect("equal")

    # Add grid
    ax.grid(True, alpha=0.3)

    # Add legend if we have items
    if legend_handles:
        ax.legend(
            handles=legend_handles[:10],  # Limit to 10 items
            labels=legend_labels[:10],
            loc="best",
            fontsize="small",
        )

    # Auto-scale with some padding
    ax.autoscale(enable=True, tight=False)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xpadding = (xlim[1] - xlim[0]) * 0.05 if xlim[1] != xlim[0] else 1.0
    ypadding = (ylim[1] - ylim[0]) * 0.05 if ylim[1] != ylim[0] else 1.0
    ax.set_xlim(xlim[0] - xpadding, xlim[1] + xpadding)
    ax.set_ylim(ylim[0] - ypadding, ylim[1] + ypadding)

    # Save or show
    if filename:
        fig.savefig(filename, dpi=dpi, bbox_inches="tight")

    if show:
        plt.show()

    return fig

"""Tests for cross-section export functionality."""

import tempfile
from pathlib import Path

import matplotlib.figure
import pytest

import gdsfactory as gf
from gdsfactory.export.to_cross_section import to_cross_section
from gdsfactory.gpdk.layer_map import LAYER
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer


def get_layer_stack() -> LayerStack:
    """Returns dummy LayerStack for testing."""
    return LayerStack(
        layers=dict(
            substrate=LayerLevel(
                layer=LogicalLayer(layer=(1, 0)),
                thickness=1.0,
                zmin=-1.0,
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


def test_to_cross_section_basic() -> None:
    """Test basic cross-section generation."""
    c = gf.components.rectangle(size=(10, 10), layer=(2, 0))
    fig = to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=get_layer_stack(),
    )
    assert isinstance(fig, matplotlib.figure.Figure)


def test_to_cross_section_saves_file() -> None:
    """Test that cross-section saves to file."""
    c = gf.components.rectangle(size=(10, 10), layer=(2, 0))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        result = to_cross_section(
            c,
            plane_position=5.0,
            plane_direction="y",
            layer_stack=get_layer_stack(),
            filename=tmp_path,
        )
        # When filename is provided, returns None
        assert result is None
        # Check file exists
        assert tmp_path.exists()
    finally:
        # Clean up
        if tmp_path.exists():
            tmp_path.unlink()


def test_to_cross_section_both_directions() -> None:
    """Test cross-section generation for both x and y directions."""
    c = gf.components.rectangle(size=(10, 10), layer=(2, 0))

    # Test x-direction
    fig_x = to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=get_layer_stack(),
    )
    assert isinstance(fig_x, matplotlib.figure.Figure)

    # Test y-direction
    fig_y = to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="y",
        layer_stack=get_layer_stack(),
    )
    assert isinstance(fig_y, matplotlib.figure.Figure)


def test_to_cross_section_no_intersection() -> None:
    """Test that ValueError is raised when plane doesn't intersect component."""
    c = gf.components.rectangle(size=(10, 10), layer=(2, 0))

    # Plane far away from component
    with pytest.raises(ValueError, match="No layers found at plane_position"):
        to_cross_section(
            c,
            plane_position=100.0,
            plane_direction="x",
            layer_stack=get_layer_stack(),
        )


def test_to_cross_section_with_component_input() -> None:
    """Test cross-section generation directly from Component (not GDS file)."""
    # Test that we can also pass a Component directly
    # The function signature currently expects gdspath, but we should support Component too
    # For now, we save to temp GDS and test that flow
    c = gf.components.rectangle(size=(10, 10), layer=(2, 0))

    with tempfile.TemporaryDirectory() as tmpdir:
        gdspath = Path(tmpdir) / "test.gds"
        c.write_gds(gdspath)

        fig = to_cross_section(
            gdspath,
            plane_position=5.0,
            plane_direction="x",
            layer_stack=get_layer_stack(),
        )
        assert isinstance(fig, matplotlib.figure.Figure)


def test_to_cross_section_exclude_layers() -> None:
    """Test cross-section with excluded layers."""
    # Create component with only one layer that will be excluded
    c = gf.Component()
    c.add_polygon([(0, 0), (10, 0), (10, 10), (0, 10)], layer=(1, 0))

    # Create LayerStack with only layer (1, 0)
    test_layer_stack = LayerStack(
        layers=dict(
            substrate=LayerLevel(
                layer=LogicalLayer(layer=(1, 0)),
                thickness=1.0,
                zmin=-1.0,
                material="si",
                mesh_order=99,
            )
        )
    )

    # Test with excluding the only layer (1, 0) - this should raise ValueError
    with pytest.raises(ValueError, match="No layers found"):
        to_cross_section(
            c,
            plane_position=5.0,
            plane_direction="x",
            layer_stack=test_layer_stack,
            exclude_layers=[(1, 0)],
        )


def test_to_cross_section_multiple_layers() -> None:
    """Test cross-section with multiple layers in LayerStack."""
    c = gf.components.rectangle(size=(10, 10), layer=(2, 0))

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
            clad=LayerLevel(
                layer=LogicalLayer(layer=(3, 0)),
                thickness=3.0,
                zmin=0.22,
                material="sio2",
                mesh_order=1,
            ),
        )
    )

    fig = to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=layer_stack,
    )
    assert isinstance(fig, matplotlib.figure.Figure)

#!/usr/bin/env python3
"""
Complete Standalone Example: GDS Cross-Section Generation

This example demonstrates how to generate vertical cross-section images
from GDS files using gdsfactory's to_cross_section() function.

Requirements:
    pip install gdsfactory[full]

Usage:
    python cross_section_example.py
"""

from pathlib import Path
from gdsfactory.export import to_cross_section
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer


# =============================================================================
# METHOD 1: Using GDS file path with custom LayerStack
# =============================================================================

def example_1_from_gds_file():
    """Generate cross-section from a GDS file."""
    print("\n" + "="*60)
    print("Example 1: Cross-Section from GDS File")
    print("="*60)

    # Step 1: Define a LayerStack that matches your GDS file layers
    # The LayerStack defines the thickness and z-position of each layer
    layer_stack = LayerStack(
        layers=dict(
            # Substrate layer (e.g., silicon wafer)
            substrate=LayerLevel(
                layer=LogicalLayer(layer=(1, 0)),
                thickness=2.0,      # 2 microns thick
                zmin=-2.0,          # Starts at z = -2 microns
                material="si",      # Silicon
                mesh_order=99,
            ),
            # Core waveguide layer
            core=LayerLevel(
                layer=LogicalLayer(layer=(2, 0)),
                thickness=0.22,     # 220 nanometers thick
                zmin=0.0,           # Starts at z = 0
                material="si",      # Silicon
                mesh_order=2,
            ),
            # Cladding layer (e.g., oxide)
            clad=LayerLevel(
                layer=LogicalLayer(layer=(3, 0)),
                thickness=3.0,      # 3 microns thick
                zmin=0.22,          # Starts on top of core
                material="sio2",    # Silicon dioxide
                mesh_order=1,
            ),
        )
    )

    # Step 2: Generate cross-section from GDS file
    # Replace with your actual GDS file path
    gdspath = "path/to/your/design.gds"

    # The function will:
    # - Import the GDS file
    # - Extrude layers to 3D using LayerStack
    # - Slice with plane at specified position
    # - Save PNG image

    print(f"To generate cross-section from GDS file:")
    print(f"  gdspath = '{gdspath}'")
    print(f"  plane_position = 5.0 (slice at x = 5 microns)")
    print(f"  plane_direction = 'x' (show y-z plane)")
    print(f"\nCall:")
    print(f"  to_cross_section(")
    print(f"      '{gdspath}',")
    print(f"      plane_position=5.0,")
    print(f"      plane_direction='x',")
    print(f"      layer_stack=layer_stack,")
    print(f"      filename='output.png'")
    print(f"  )")


# =============================================================================
# METHOD 2: Using Component object with active PDK
# =============================================================================

def example_2_from_component():
    """Generate cross-section from a Component object."""
    print("\n" + "="*60)
    print("Example 2: Cross-Section from Component")
    print("="*60)

    import gdsfactory as gf
    from gdsfactory.gpdk import PDK

    # Activate PDK first (required)
    PDK.activate()

    # Create a simple component (straight waveguide)
    c = gf.components.straight(length=10)

    # Use PDK's built-in layer stack
    layer_stack = gf.pdk.get_layer_stack()

    # Generate cross-section and save to file
    fig = to_cross_section(
        c,
        plane_position=5.0,      # Slice at x = 5 microns
        plane_direction="x",     # Show y-z plane
        layer_stack=layer_stack,
        filename="cross_section_output.png",
        dpi=150,
    )

    print(f"✓ Cross-section saved to: cross_section_output.png")
    return fig


# =============================================================================
# METHOD 3: Both X and Y directions
# =============================================================================

def example_3_both_directions():
    """Generate cross-sections in both directions."""
    print("\n" + "="*60)
    print("Example 3: Both X and Y Directions")
    print("="*60)

    import gdsfactory as gf
    from gdsfactory.gpdk import PDK

    PDK.activate()

    # Create a rectangular component
    c = gf.components.rectangle(size=(10, 20))

    # Get PDK layer stack
    layer_stack = gf.pdk.get_layer_stack()

    # X-direction: shows y-z plane at x = 5
    # (slice perpendicular to x-axis)
    to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=layer_stack,
        filename="cross_section_x_direction.png",
    )
    print(f"✓ Saved: cross_section_x_direction.png (shows y-z plane)")

    # Y-direction: shows x-z plane at y = 10
    # (slice perpendicular to y-axis)
    to_cross_section(
        c,
        plane_position=10.0,
        plane_direction="y",
        layer_stack=layer_stack,
        filename="cross_section_y_direction.png",
    )
    print(f"✓ Saved: cross_section_y_direction.png (shows x-z plane)")


# =============================================================================
# METHOD 4: Multi-layer realistic SOI stack
# =============================================================================

def example_4_multi_layer_soi():
    """Generate cross-section with realistic SOI layer stack."""
    print("\n" + "="*60)
    print("Example 4: Realistic SOI Multi-Layer Stack")
    print("="*60)

    import gdsfactory as gf
    from gdsfactory.gpdk import PDK

    PDK.activate()

    # Create a component
    c = gf.components.straight(length=10)

    # Define realistic SOI (Silicon-on-Insulator) LayerStack
    layer_stack = LayerStack(
        layers=dict(
            # Silicon substrate (handle wafer)
            substrate=LayerLevel(
                layer=LogicalLayer(layer=(1, 0)),
                thickness=10.0,
                zmin=-13.0,
                material="si",
                mesh_order=99,
            ),
            # Buried oxide (BOX)
            box=LayerLevel(
                layer=LogicalLayer(layer=(2, 0)),
                thickness=3.0,
                zmin=-3.0,
                material="sio2",
                mesh_order=98,
            ),
            # Silicon device layer (waveguide core)
            core=LayerLevel(
                layer=LogicalLayer(layer=(3, 0)),
                thickness=0.22,
                zmin=0.0,
                material="si",
                mesh_order=2,
            ),
            # Oxide cladding
            clad=LayerLevel(
                layer=LogicalLayer(layer=(4, 0)),
                thickness=3.0,
                zmin=0.22,
                material="sio2",
                mesh_order=1,
            ),
        )
    )

    # Create multi-layer component
    multi_layer_c = gf.Component()
    multi_layer_c << c  # Add waveguide

    # Generate cross-section
    to_cross_section(
        multi_layer_c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=layer_stack,
        filename="cross_section_soi.png",
        dpi=300,
    )

    print(f"✓ Saved: cross_section_soi.png (300 DPI)")
    print(f"  Layer stack with {len(layer_stack.layers)} layers:")
    for name, level in layer_stack.layers.items():
        print(f"    {name:12s}: material={level.material:6s}, "
              f"thickness={level.thickness:6.2f}µm, zmin={level.zmin:7.2f}µm")


# =============================================================================
# METHOD 5: Multiple cross-sections at different positions
# =============================================================================

def example_5_multiple_slices():
    """Generate multiple cross-sections along a waveguide."""
    print("\n" + "="*60)
    print("Example 5: Multiple Cross-Sections Along Waveguide")
    print("="*60)

    import gdsfactory as gf
    from gdsfactory.gpdk import PDK

    PDK.activate()

    # Create a long waveguide
    c = gf.components.straight(length=50)

    layer_stack = gf.pdk.get_layer_stack()

    # Generate cross-sections at multiple positions
    positions = [5, 15, 25, 35, 45]

    for pos in positions:
        filename = f"cross_section_x_{pos:02d}.png"
        to_cross_section(
            c,
            plane_position=float(pos),
            plane_direction="x",
            layer_stack=layer_stack,
            filename=filename,
        )
        print(f"✓ Saved: {filename}")

    print(f"  Generated {len(positions)} cross-section images")


# =============================================================================
# METHOD 6: Return Figure without saving (for further processing)
# =============================================================================

def example_6_return_figure():
    """Generate cross-section and return Figure object."""
    print("\n" + "="*60)
    print("Example 6: Return Figure (for further processing)")
    print("="*60)

    import gdsfactory as gf
    from gdsfactory.gpdk import PDK
    import matplotlib.pyplot as plt

    PDK.activate()

    # Create component
    c = gf.components.straight(length=10)

    layer_stack = gf.pdk.get_layer_stack()

    # Generate cross-section (returns Figure, doesn't save)
    fig = to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=layer_stack,
        # No filename parameter -> returns Figure
    )

    # Now you can modify the figure
    ax = fig.axes[0]
    ax.set_title("Custom Title: Cross-Section at x=5µm", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.5, linestyle='--')

    # Save with custom settings
    fig.savefig("cross_section_custom.png", dpi=200, bbox_inches='tight')
    plt.close(fig)

    print(f"✓ Saved: cross_section_custom.png (with custom styling)")
    return fig


# =============================================================================
# METHOD 7: Excluding specific layers
# =============================================================================

def example_7_exclude_layers():
    """Generate cross-section excluding certain layers."""
    print("\n" + "="*60)
    print("Example 7: Excluding Specific Layers")
    print("="*60)

    import gdsfactory as gf
    from gdsfactory.gpdk import PDK

    PDK.activate()

    # Create custom multi-layer component
    c = gf.Component()
    c.add_polygon([(0, 0), (10, 0), (10, 10), (0, 10)], layer=(1, 0))
    c.add_polygon([(2, 2), (8, 2), (8, 8), (2, 8)], layer=(2, 0))

    # Create LayerStack with multiple layers
    layer_stack = LayerStack(
        layers=dict(
            layer1=LayerLevel(
                layer=LogicalLayer(layer=(1, 0)),
                thickness=1.0,
                zmin=-1.0,
                material="si",
                mesh_order=2,
            ),
            layer2=LayerLevel(
                layer=LogicalLayer(layer=(2, 0)),
                thickness=0.22,
                zmin=0.0,
                material="si",
                mesh_order=1,
            ),
        )
    )

    # Generate cross-section including all layers
    to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=layer_stack,
        filename="cross_section_all_layers.png",
    )
    print(f"✓ Saved: cross_section_all_layers.png (all layers)")

    # Exclude layer (1, 0) from cross-section
    to_cross_section(
        c,
        plane_position=5.0,
        plane_direction="x",
        layer_stack=layer_stack,
        exclude_layers=[(1, 0)],  # Exclude layer (1, 0)
        filename="cross_section_no_layer1.png",
    )
    print(f"✓ Saved: cross_section_no_layer1.png (layer 1/0 excluded)")


# =============================================================================
# MAIN: Run all examples
# =============================================================================

def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("GDS Cross-Section Generation - Complete Examples")
    print("="*60)

    # Run examples
    example_1_from_gds_file()
    example_2_from_component()
    example_3_both_directions()
    example_4_multi_layer_soi()
    example_5_multiple_slices()
    example_6_return_figure()
    example_7_exclude_layers()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
    print("\nGenerated files:")
    print("  - cross_section_output.png")
    print("  - cross_section_x_direction.png")
    print("  - cross_section_y_direction.png")
    print("  - cross_section_soi.png")
    print("  - cross_section_x_XX.png (multiple)")
    print("  - cross_section_custom.png")
    print("  - cross_section_all_layers.png")
    print("  - cross_section_no_layer1.png")


if __name__ == "__main__":
    main()

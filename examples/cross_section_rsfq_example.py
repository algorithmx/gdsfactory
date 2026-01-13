#!/usr/bin/env python3
"""
RSFQ Cross-Section Example Using MIT LL RSFQ Library

This example demonstrates how to generate cross-section images from the
MIT Lincoln Laboratory RSFQ (Rapid Single Flux Quantum) cell library.

PDK Path: /path/to/sc_transmission_line/Rapid_Single_Flux_Quantum/RSFQlib/RSFQlib/

Requirements:
    pip install gdsfactory[full]

The RSFQ library uses a multi-layer superconducting process with:
- Multiple metal layers (M0-M7)
- Via layers (I0-I6)
- Josephson junction layers (J5, R5, C5J, C5R)
- Ground and power planes

Typical MIT LL SFQ process layer stack (hypothetical values - for demonstration):
- Substrate: Silicon wafer
- M0: Ground plane (bottom metal)
- I0-I6: Vias between metal layers
- M1-M7: Metal routing layers
- J5: Josephson junction layer
- R5: Resistor layer
"""

from pathlib import Path
from gdsfactory.export import to_cross_section
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer
import gdsfactory as gf
from gdsfactory.gpdk import PDK

# =============================================================================
# RSFQ PDK Configuration
# =============================================================================

RSFQ_PDK_PATH = Path("/home/dabajabaza/Nutstore/Work/Project/sc_transmission_line/Rapid_Single_Flux_Quantum/RSFQlib/RSFQlib")

# Example GDS file from RSFQ library
RSFQ_GDS_FILE = RSFQ_PDK_PATH / "mitll_PTLRX-SFQDC/THmitll_PTLRX-SFQDC_v3p0.gds"


# =============================================================================
# METHOD 1: Define hypothetical MIT LL SFQ LayerStack
# =============================================================================

def get_rsfq_layer_stack_hypothetical():
    """
    Define a hypothetical LayerStack for MIT LL SFQ process.

    NOTE: These are EXAMPLE values for demonstration.
    Actual thickness values should be obtained from:
    - MIT LL process documentation
    - PDK specification files
    - Process design kit documentation

    IMPORTANT: Layer tuples must match the ACTUAL GDS layer numbers.
    Use component.kcl.layer_infos() to discover the layer numbers in your GDS file.

    Typical SFQ process (hypothetical values):
    - M0: Ground plane (200-300 nm)
    - M1-M7: Routing layers (200-400 nm each)
    - J5: Josephson junction barrier (~few nm)
    - I0-I6: Via layers
    """

    # Hypothetical MIT LL SFQ LayerStack with CORRECTED layer numbers
    # Actual GDS layers with shapes: (1,0), (2,0), (20,0), (21,0), (40,0), (41,0), (50,0), (60,0), (61,0), (70,0)
    layer_stack = LayerStack(
        layers=dict(
            # Substrate
            substrate=LayerLevel(
                layer=LogicalLayer(layer=(1, 0)),
                thickness=500.0,    # 500 µm wafer
                zmin=-500.0,
                material="si",
                mesh_order=100,
            ),

            # M0 - Ground plane (bottom metal) - GDS layer (2, 0)
            m0=LayerLevel(
                layer=LogicalLayer(layer=(2, 0)),
                thickness=0.3,      # 300 nm
                zmin=0.0,
                material="nb",      # Niobium
                mesh_order=90,
            ),

            # M1 - First routing layer - GDS layer (20, 0)
            m1=LayerLevel(
                layer=LogicalLayer(layer=(20, 0)),
                thickness=0.2,      # 200 nm
                zmin=0.4,
                material="nb",
                mesh_order=80,
            ),

            # M2 - Second routing layer - GDS layer (21, 0)
            m2=LayerLevel(
                layer=LogicalLayer(layer=(21, 0)),
                thickness=0.2,
                zmin=0.7,
                material="nb",
                mesh_order=70,
            ),

            # M4 - Fourth routing layer (ground plane) - GDS layer (40, 0)
            m4=LayerLevel(
                layer=LogicalLayer(layer=(40, 0)),
                thickness=0.2,
                zmin=1.3,
                material="nb",
                mesh_order=50,
            ),

            # M5 - Fifth routing layer (Junction layer) - GDS layer (41, 0)
            m5=LayerLevel(
                layer=LogicalLayer(layer=(41, 0)),
                thickness=0.25,     # 250 nm
                zmin=1.6,
                material="nb",
                mesh_order=40,
            ),

            # J5 - Josephson junction layer - GDS layer (50, 0)
            j5=LayerLevel(
                layer=LogicalLayer(layer=(50, 0)),
                thickness=0.003,    # ~3 nm barrier
                zmin=1.85,
                material="alox",    # Aluminum oxide barrier
                mesh_order=10,
            ),

            # M6 - Sixth routing layer - GDS layer (60, 0)
            m6=LayerLevel(
                layer=LogicalLayer(layer=(60, 0)),
                thickness=0.35,     # 350 nm
                zmin=2.0,
                material="nb",
                mesh_order=30,
            ),

            # M7 - Top metal - GDS layer (61, 0)
            m7=LayerLevel(
                layer=LogicalLayer(layer=(61, 0)),
                thickness=0.5,      # 500 nm
                zmin=2.5,
                material="nb",
                mesh_order=20,
            ),

            # Via layer - GDS layer (70, 0)
            via=LayerLevel(
                layer=LogicalLayer(layer=(70, 0)),
                thickness=0.2,
                zmin=1.0,
                material="nb",
                mesh_order=60,
            ),
        )
    )

    return layer_stack


# =============================================================================
# METHOD 2: Minimal LayerStack for quick visualization
# =============================================================================

def get_rsfq_layer_stack_minimal():
    """
    Define MIT LL SFQ5ee Process LayerStack based on public specifications.

    SOURCE: Tolpygo et al., "Advanced Fabrication Processes for Superconducting
    Very Large Scale Integrated Circuits", IEEE Trans. Appl. Supercond., vol. 26, no. 3, 2016.
    https://apps.dtic.mil/sti/trecms/pdf/AD1034542.pdf

    MIT LL SFQ5ee Process Specifications (Table I in the paper):

    Layer  | Material       | Thickness (nm) | Description
    -------|----------------|---------------|------------
    M0     | Nb             | 200 ± 15      | Bottom metal/ground plane
    I0     | SiO2           | 200 ± 30      | Interlayer dielectric
    M1     | Nb             | 200 ± 15      | Metal layer 1
    I1     | SiO2           | 200 ± 30      | Interlayer dielectric
    M2     | Nb             | 200 ± 15      | Metal layer 2
    I2     | SiO2           | 200 ± 30      | Interlayer dielectric
    M3     | Nb             | 200 ± 15      | Metal layer 3
    I3     | SiO2           | 200 ± 30      | Interlayer dielectric
    M4     | Nb             | 200 ± 15      | Metal layer 4 (ground plane)
    I4     | SiO2           | 200 ± 30      | Interlayer dielectric
    M5     | Nb             | 135 ± 15      | Metal layer 5 (junction base)
    J5     | AlOx/Nb        | ~170 ± 15    | Josephson junction barrier
    A5a    | anodic oxide   | ~170 ± 15    | Mixed anodic oxide
    I5a    | SiO2           | 170 ± 15      | Via dielectric
    A5b    | SiO2           | 40 ± 270     | Anodized oxide
    I5b    | SiO2           | 170 ± 15      | Via dielectric
    R5     | MoNx (6 Ω/sq) | 40 ± 5        | Resistor layer
    C5     | SiO2           | 70 ± 5        | Dielectric
    M6     | Nb             | 200 ± 15      | Metal layer 6
    I6     | SiO2           | 200 ± 30      | Interlayer dielectric
    M7     | Nb             | 200 ± 15      | Metal layer 7 (top metal)
    I7     | SiO2           | 200 ± 30      | Interlayer dielectric
    M8     | Au/Pt/Ti       | 250 ± 30      | Bond pads

    NOTES:
    - All Nb metal layers are 200 nm except M5 (135 nm, junction base electrode)
    - All SiO2 dielectric layers are 200 nm between metal layers
    - Minimum feature size: 350 nm (critical), 500 nm (other)
    - JJs are placed between M5 and M6
    - Ground plane is typically M4

    IMPORTANT: The layer tuples below are the ACTUAL GDS layer numbers from the
    RSFQ library file (THmitll_PTLRX-SFQDC_v3p0.gds). These were determined by
    inspecting the GDS file with component.kcl.layer_infos().

    Actual GDS layers with shapes (layer_tuple -> description):
        (1, 0)  -> Substrate/boundary
        (2, 0)  -> M0 ground plane (56 polygons)
        (20, 0) -> M1 metal layer (29 polygons)
        (21, 0) -> M2 metal layer (58 polygons)
        (40, 0) -> M4 ground plane (89 polygons)
        (41, 0) -> M5 junction base (41 polygons)
        (50, 0) -> J5 Josephson junction (97 polygons)
        (60, 0) -> M6 metal layer (138 polygons)
        (61, 0) -> M7 top metal (39 polygons)
        (70, 0) -> Via/interconnect layer (75 polygons)

    WARNING: The previous layer numbers (3, 22, 26, 47, 49) were WRONG because
    they were the internal layer_index values from get_polygons(), not the actual
    GDS layer numbers. This caused all cross-sections to appear identical since
    only the substrate layer (1, 0) was being rendered.

    NOTE: Only layers with corresponding LayerViews in the generic PDK will be
    rendered. The following layers from this GDS file have LayerViews:
    (1, 0), (2, 0), (20, 0), (21, 0), (40, 0), (41, 0)

    Layers like (50, 0), (60, 0), (61, 0), (70, 0) do NOT have LayerViews in
    the generic PDK and will be skipped. To render these, you need to either:
    1. Create a custom LayerViews file for the RSFQ process, or
    2. Modify the generic PDK to include these layers
    """

    layer_stack = LayerStack(
        layers=dict(
            # Layer (1, 0) - Substrate/wafer boundary - HAS LayerView
            substrate=LayerLevel(
                layer=LogicalLayer(layer=(1, 0)),
                thickness=10.0,     # Representation
                zmin=-10.0,
                material="si",
                mesh_order=100,
            ),

            # Layer (2, 0) - M0 ground plane - HAS LayerView
            # SFQ5ee: 200 nm Nb
            m0=LayerLevel(
                layer=LogicalLayer(layer=(2, 0)),
                thickness=0.2,      # 200 nm
                zmin=0.0,
                material="nb",
                mesh_order=90,
            ),

            # Layer (20, 0) - M1 metal layer - HAS LayerView
            # SFQ5ee: 200 nm Nb
            m1=LayerLevel(
                layer=LogicalLayer(layer=(20, 0)),
                thickness=0.2,
                zmin=0.25,
                material="nb",
                mesh_order=85,
            ),

            # Layer (21, 0) - M2 metal layer - HAS LayerView
            # SFQ5ee: 200 nm Nb
            m2=LayerLevel(
                layer=LogicalLayer(layer=(21, 0)),
                thickness=0.2,
                zmin=0.5,
                material="nb",
                mesh_order=80,
            ),

            # Layer (40, 0) - M4 ground plane - HAS LayerView
            # SFQ5ee: 200 nm Nb
            m4=LayerLevel(
                layer=LogicalLayer(layer=(40, 0)),
                thickness=0.2,
                zmin=1.0,
                material="nb",
                mesh_order=70,
            ),

            # Layer (41, 0) - M5 junction base electrode - HAS LayerView
            # SFQ5ee: 135 nm Nb
            m5=LayerLevel(
                layer=LogicalLayer(layer=(41, 0)),
                thickness=0.135,    # 135 nm
                zmin=1.25,
                material="nb",
                mesh_order=65,
            ),

            # NOTE: The following layers do NOT have LayerViews in generic PDK
            # and will be skipped during cross-section rendering:
            # - (50, 0) - J5 Josephson junction (97 polygons)
            # - (60, 0) - M6 metal layer (138 polygons)
            # - (61, 0) - M7 top metal (39 polygons)
            # - (70, 0) - Via/interconnect layer (75 polygons)
        )
    )

    return layer_stack


# =============================================================================
# EXAMPLE 1: Load RSFQ GDS and generate cross-section
# =============================================================================

def example_1_rsfq_cross_section():
    """Generate multiple cross-sections from RSFQ GDS file."""
    print("\n" + "="*60)
    print("Example 1: RSFQ Multiple Cross-Sections")
    print("="*60)

    # Check if GDS file exists
    if not RSFQ_GDS_FILE.exists():
        print(f"✗ RSFQ GDS file not found: {RSFQ_GDS_FILE}")
        print("  Please update RSFQ_PDK_PATH in the script")
        return None

    print(f"RSFQ GDS file: {RSFQ_GDS_FILE}")

    # Activate PDK
    PDK.activate()

    # Get LayerStack (use minimal for now)
    layer_stack = get_rsfq_layer_stack_minimal()

    # Import GDS to get bounds
    c = gf.import_gds(str(RSFQ_GDS_FILE))
    polygons = c.get_polygons_points()

    # Get bounding box
    all_x, all_y = [], []
    for _layer_idx, polys in polygons.items():
        for poly in polys:
            for p in poly:
                all_x.append(p[0])
                all_y.append(p[1])

    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)

    print(f"  X range: {x_min:.2f} to {x_max:.2f} µm")
    print(f"  Y range: {y_min:.2f} to {y_max:.2f} µm")

    # Generate multiple cross-sections along X axis
    num_slices = 10  # Generate 10 cross-sections
    print(f"\nGenerating {num_slices} cross-sections along X axis...")

    print(f"  Using layers from LayerStack: {list(layer_stack.layers.keys())}")
    print(f"  Note: Only layers 1,3,22,26,47,49 are in both GDS and default LayerViews\n")

    for i in range(num_slices):
        # Calculate position: evenly spaced along X axis
        # Use padding to avoid exact edges
        padding = (x_max - x_min) * 0.02  # 2% padding on each side
        x_min_padded = x_min + padding
        x_max_padded = x_max - padding
        x_pos = x_min_padded + (x_max_padded - x_min_padded) * i / max(1, num_slices - 1)

        # Generate filename
        filename = f"rsfq_cross_section_x_{i:02d}.png"

        # Generate cross-section with vertical exaggeration for better visibility
        # The layer thicknesses are in the range 0.1-10 µm while horizontal span is ~40 µm
        # A vertical exaggeration of 10-20x makes the layers more visible
        to_cross_section(
            str(RSFQ_GDS_FILE),
            plane_position=x_pos,
            plane_direction="x",
            layer_stack=layer_stack,
            layer_views=None,  # Use default PDK LayerViews
            filename=filename,
            dpi=200,
            vertical_exaggeration=15.0,  # Stretch vertical direction 15x
        )

        print(f"  [{i+1:2d}/{num_slices}] x = {x_pos:7.2f} µm → {filename}")

    print(f"\n✓ Generated {num_slices} cross-section images")
    return None


# =============================================================================
# EXAMPLE 2: Multiple cross-sections
# =============================================================================

def example_2_rsfq_multiple_slices():
    """Generate multiple cross-sections along RSFQ device."""
    print("\n" + "="*60)
    print("Example 2: RSFQ Multiple Cross-Sections")
    print("="*60)

    if not RSFQ_GDS_FILE.exists():
        print(f"✗ RSFQ GDS file not found: {RSFQ_GDS_FILE}")
        return

    PDK.activate()
    layer_stack = get_rsfq_layer_stack_minimal()

    # Import and get bounds
    c = gf.import_gds(str(RSFQ_GDS_FILE))
    polygons = c.get_polygons_points()

    all_x = []
    for _layer_idx, polys in polygons.items():
        for poly in polys:
            for p in poly:
                all_x.append(p[0])

    x_min, x_max = min(all_x), max(all_x)

    # Generate 5 cross-sections
    num_slices = 5
    positions = [x_min + (x_max - x_min) * i / (num_slices - 1) for i in range(num_slices)]

    for i, pos in enumerate(positions):
        filename = f"rsfq_cross_section_{i+1}.png"
        to_cross_section(
            str(RSFQ_GDS_FILE),
            plane_position=pos,
            plane_direction="x",
            layer_stack=layer_stack,
            filename=filename,
            dpi=150,
        )
        print(f"✓ Saved: {filename} (x = {pos:.2f} µm)")


# =============================================================================
# EXAMPLE 3: Layer analysis
# =============================================================================

def example_3_layer_analysis():
    """Analyze layers in RSFQ GDS file."""
    print("\n" + "="*60)
    print("Example 3: RSFQ Layer Analysis")
    print("="*60)

    if not RSFQ_GDS_FILE.exists():
        print(f"✗ RSFQ GDS file not found: {RSFQ_GDS_FILE}")
        return

    PDK.activate()
    c = gf.import_gds(str(RSFQ_GDS_FILE))

    print(f"\nAnalyzing: {RSFQ_GDS_FILE.name}")
    print(f"Component name: {c.name}")

    polygons = c.get_polygons_points()

    print(f"\nLayer Statistics:")
    print("Layer | Polygons | Description (based on SFQ5ee process)")
    print("-" * 60)

    # Corrected layer descriptions based on actual GDS layer numbers
    # These correspond to the actual MIT LL SFQ layer mapping
    layer_descriptions = {
        1: "Substrate/wafer boundary",
        2: "M0 - Ground plane (bottom metal)",
        10: "I0 - Via layer",
        11: "I1 - Via layer",
        19: "Passive interconnect",
        20: "M1 - Metal 1",
        21: "M2 - Metal 2",
        30: "I2 - Via layer",
        31: "I3 - Via layer",
        40: "M4 - Ground plane",
        41: "M5 - Junction base electrode",
        50: "J5 - Josephson junctions",
        51: "R5 - Resistors",
        52: "C5 - Capacitor dielectric",
        54: "I5 - Via layer",
        55: "A5 - Anodized oxide",
        56: "I5b - Via layer",
        60: "M6 - Metal 6 (routing)",
        61: "M7 - Metal 7 (top metal)",
        70: "Via/interconnect layer",
    }

    for layer_idx in sorted(polygons.keys()):
        polys = polygons[layer_idx]
        desc = layer_descriptions.get(layer_idx, "Unknown")
        print(f"  {layer_idx:3d}   |   {len(polys):4d}   | {desc}")

    print(f"\nTotal layers with geometry: {len(polygons)}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run all RSFQ cross-section examples."""
    print("\n" + "="*60)
    print("RSFQ Cross-Section Examples")
    print("="*60)
    print(f"\nRSFQ PDK Path: {RSFQ_PDK_PATH}")

    # Run examples
    example_3_layer_analysis()
    example_1_rsfq_cross_section()
    # example_2_rsfq_multiple_slices()  # Uncomment for multiple slices

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nGenerated files:")
    print("  - rsfq_cross_section_x_00.png to rsfq_cross_section_x_09.png")
    print("    (10 cross-sections evenly spaced along X axis)")
    print("\nIMPORTANT NOTES:")
    print("  1. Layer thickness values in this example are HYPOTHETICAL")
    print("  2. For actual MIT LL process specs, consult:")
    print("     - MIT LL SFQ design documentation")
    print("     - PDK layer specification files")
    print("     - Process design kit manuals")
    print("  3. The LayerStack should be customized with actual process data")


if __name__ == "__main__":
    main()

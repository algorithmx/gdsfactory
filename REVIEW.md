# REVIEW.md

This file provides guidance to working with code in this repository.

## Project Overview

GDSFactory is a Python library for designing chips (Photonics, Analog, Quantum, MEMS), PCBs, and 3D-printable objects. It transforms Python code into CAD files (GDS, OASIS, STL, GERBER) for fabrication.

- Python 3.11-3.13 required (Python 3.10 support dropped)
- Built on KLayout C++ library for high performance
- 3M+ downloads, 105+ contributors

## Development Commands

### Setup

```bash
# Clone repository and test data
git clone git@github.com:YourUserName/gdsfactory.git
cd gdsfactory
git clone https://github.com/gdsfactory/gdsfactory-test-data.git -b test_klayout test-data-gds

# Install dependencies (using uv)
uv venv --python 3.12
uv sync --extra docs --extra dev

# Install pre-commit hooks
uv run pre-commit install
```

### Testing

```bash
# Run all tests
pytest -s

# Run with coverage
pytest --cov=gdsfactory -s

# Regenerate regression reference files
pytest --force-regen -s

# Run a specific test file
pytest tests/components/test_components.py -s

# Run a specific test
pytest tests/components/test_components.py::test_gds -s
```

### Code Quality

```bash
# Run pre-commit checks manually
pre-commit run --all-files

# Format with ruff
ruff check --fix .
ruff format .

# Type checking with mypy
mypy gdsfactory
```

### CLI Commands

```bash
gf build                    # Build components from YAML
gf watch                    # File watching for auto-reload
gf write-cells <gds>        # Export cells to separate GDS files
gf merge-gds                # Merge multiple GDS files
gf layermap-to-dataclass    # Convert KLayout layer maps
gf show <gds>               # Show GDS in klive
gf diff <gds1> <gds2>       # Compare two layout files
gf gds-diff <gds1> <gds2>   # Show boolean difference between GDS files
gf from-updk <yaml>         # Generate PDK from uPDK YAML specification
gf install-klayout-genericpdk # Install KLayout generic PDK
gf install-git-diff         # Install git diff for GDS files
gf version                  # Show plugin versions
```

## Architecture

### Core Abstractions

- **Component** (`gdsfactory/component.py`): Canvas for geometry (polygons, instances, ports). Stores settings, metadata, and design intent. Can export to GDSII, OASIS, STL, GERBER. Supports netlist generation.

- **Port** (`gdsfactory/port.py`): Connection points between components. Follow counter-clockwise naming convention. Support for optical, electrical, and custom port types.

- **CrossSection** (`gdsfactory/cross_section.py`): Defines waveguide/trace profiles. Supports parameterized width/offset functions, layer assignments and port definitions.

- **Pdk** (`gdsfactory/pdk.py`): Encapsulates process-specific knowledge. Manages layers, cross-sections, and component libraries. Active PDK switching capability.

- **LayerStack** (`gdsfactory/technology/layer_stack.py`): Defines vertical layer stack for 3D extrusion and cross-section generation.

### Module Organization

```
gdsfactory/
├── components/         # Parametric component library (bends, couplers, MMIs)
├── containers/         # Container components (padding, routing)
├── cross_section.py    # Waveguide and trace profile definitions
├── routing/            # Component connection and routing algorithms
├── technology/         # Layer definitions, layer stacks, technology abstractions
├── export/             # Export to GDS, OASIS, STL, GERBER, PNG (cross-section)
├── read/               # Import from GDS, YAML, images
├── pdk.py              # PDK management
├── samples/            # Example code and tutorials
├── examples/           # Comprehensive examples including cross-section
└── generic_tech/       # Generic technology PDK implementation (streamlined)
```

### Design Patterns

1. **Component-Based Architecture**: Each component is self-contained, can reference other components as instances, with port-based connections.

2. **PDK Abstraction**: Process-specific knowledge encapsulated in PDKs with active PDK switching for multi-fabrication support.

3. **Parametric Design**: All components are parameterized functions; settings capture design intent and enable regression testing.

4. **Decorator-Based**: The `@cell` decorator transforms functions into cached component factories.

5. **Regression Testing**: GDS geometry comparison (XOR-based), settings regression (YAML), netlist regression.

### Key Files

- `gdsfactory/__init__.py`: Main module exports (Component, Port, PDK, etc.)
- `gdsfactory/config.py`: Configuration and version management
- `gdsfactory/_cell.py`: Cell decorator and caching logic
- `gdsfactory/difftest.py`: GDS regression testing

## Testing Strategy

### Regression Tests

Located in `tests/components/test_components.py`:

- **GDS tests**: XOR-based geometry comparison to prevent unintended changes
- **Settings tests**: YAML-based settings validation
- **Netlist tests**: YAML netlist serialization/deserialization

When GDS regressions are found, pytest with `-s` flag will step through failures interactively, allowing you to inspect differences in KLayout and accept/reject changes.

### Test Data

Reference GDS files stored in `test-data-gds/` (separate repository). Use `--force-regen` to update reference files after intentional changes.

## Export and Visualization

### Cross-Section Export

The `gdsfactory.export` module includes `to_cross_section()` for generating vertical cross-section images from GDS files or Components. This enables 3D visualization of 2D GDS layouts.

```python
from gdsfactory.export import to_cross_section

fig = to_cross_section(
    component,                # Component object or GDS file path
    plane_position=5.0,       # Slicing plane position in microns
    plane_direction="x",      # "x" for y-z plane, "y" for x-z plane
    layer_stack=None,         # Optional LayerStack specification
    filename=None,            # Save to file or return matplotlib Figure
    vertical_exaggeration=1.0, # Scale thin layers for visibility
    dpi=150,                  # Output resolution
    exclude_layers=None,      # Layers to exclude from visualization
    show=False,               # Display interactively
)
```

Features:
- Both x and y direction cross-sections (vertical slicing)
- Layer exclusion capability
- Material legends from LayerViews
- Convex hull approximation for complex shapes (documented limitation)
- Vertical exaggeration for better visualization of thin layers
- Returns matplotlib Figure or saves to PNG file
- Integration with LayerStack for 3D extrusion
- Proper error handling for non-intersecting planes

See `examples/cross_section_example.py` for comprehensive usage examples.

### Other Export Formats

- `to_3d()`: Export to 3D formats
- `to_gds()`: Export to GDSII
- `to_oas()`: Export to OASIS
- `to_stl()`: Export to STL for 3D printing
- `to_gerber()`: Export to GERBER for PCB fabrication
- `to_svg()`: Export to SVG for visualization

## Important Notes

- Import order in `__init__.py` is critical - do not change without understanding dependencies
- The `gf.c` namespace is an alias for `gf.components` (commonly used in examples)
- KLayout integration requires KLayout to be installed for visualization
- Pre-commit hooks enforce Google Python Style Guide
- Type checking uses mypy with some error codes disabled (see pyproject.toml)
- The project uses `tbump` for automated version management and `towncrier` for changelog generation
- New dependencies added: `pygit2` (Git integration), `mapbox_earcut` (polygon triangulation), `trimesh` (3D operations)
- Python 3.10 is no longer supported - minimum version is now Python 3.11

# REVIEW.md

This file provides guidance to working with code in this repository.

## Project Overview

GDSFactory is a Python library for designing chips (Photonics, Analog, Quantum, MEMS), PCBs, and 3D-printable objects. It transforms Python code into CAD files (GDS, OASIS, STL, GERBER) for fabrication.

- Python 3.11-3.13 supported
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
gf diff <gds1> <gds2>       # Compare two GDS files
gf version                  # Show plugin versions
```

## Architecture

### Core Abstractions

- **Component** (`gdsfactory/component.py`): Canvas for geometry (polygons, instances, ports). Stores settings, metadata, and design intent. Can export to GDSII, OASIS, STL, GERBER. Supports netlist generation.

- **Port** (`gdsfactory/port.py`): Connection points between components. Follow counter-clockwise naming convention. Support for optical, electrical, and custom port types.

- **CrossSection** (`gdsfactory/cross_section.py`): Defines waveguide/trace profiles. Supports parameterized width/offset functions, layer assignments and port definitions.

- **Pdk** (`gdsfactory/pdk.py`): Encapsulates process-specific knowledge. Manages layers, cross-sections, and component libraries. Active PDK switching capability.

### Module Organization

```
gdsfactory/
├── components/         # Parametric component library (bends, couplers, MMIs)
├── containers/         # Container components (padding, routing)
├── cross_section.py    # Waveguide and trace profile definitions
├── routing/            # Component connection and routing algorithms
├── technology/         # Layer definitions, layer stacks, technology abstractions
├── export/             # Export to GDS, OASIS, STL, GERBER
├── read/               # Import from GDS, YAML, images
├── pdk.py              # PDK management
├── samples/            # Example code and tutorials
└── generic_tech/       # Generic technology PDK implementation
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

## Important Notes

- Import order in `__init__.py` is critical - do not change without understanding dependencies
- The `gf.c` namespace is an alias for `gf.components` (commonly used in examples)
- KLayout integration requires KLayout to be installed for visualization
- Pre-commit hooks enforce Google Python Style Guide
- Type checking uses mypy with some error codes disabled (see pyproject.toml)

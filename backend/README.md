# Digital Farmers CMS - Backend

This is the backend module for the Digital Farmers CMS system.

## Project Structure

```
backend/
├── core/                    # Core package
│   ├── __init__.py         # Package initialization
│   └── ...                 # Other core modules
├── tests/                  # Test files
├── requirements.txt        # Project dependencies
└── setup.py               # Package configuration
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/macOS
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Development

To run tests:
```bash
pytest
```

## License

MIT

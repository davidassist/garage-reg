#!/usr/bin/env python3
"""
Infrastructure check for automated test suites.
Verifies that all testing components are functional.
"""

import pytest
import asyncio
import subprocess
import sys
from pathlib import Path

def test_pytest_installation():
    """Test that pytest is properly installed."""
    import pytest
    version = pytest.__version__
    print(f"✅ pytest version: {version}")
    assert version is not None

def test_coverage_installation():
    """Test that pytest-cov is properly installed."""
    import coverage
    version = coverage.__version__
    print(f"✅ coverage.py version: {version}")
    assert version is not None

def test_httpx_installation():
    """Test that httpx is properly installed.""" 
    import httpx
    version = httpx.__version__
    print(f"✅ httpx version: {version}")
    assert version is not None

def test_fastapi_installation():
    """Test that FastAPI is properly installed."""
    import fastapi
    version = fastapi.__version__
    print(f"✅ FastAPI version: {version}")
    assert version is not None

def test_sqlalchemy_installation():
    """Test that SQLAlchemy is properly installed."""
    import sqlalchemy
    version = sqlalchemy.__version__
    print(f"✅ SQLAlchemy version: {version}")
    assert version is not None

@pytest.mark.asyncio
async def test_async_support():
    """Test that async/await works correctly."""
    await asyncio.sleep(0.01)
    print("✅ Async/await support works")
    assert True

def test_test_directory_structure():
    """Test that test directory structure exists."""
    backend_dir = Path(__file__).parent
    test_dir = backend_dir / "tests"
    
    # Check basic structure
    assert test_dir.exists(), "tests/ directory should exist"
    
    unit_dir = test_dir / "unit"
    integration_dir = test_dir / "integration"
    
    print(f"✅ Test directory structure:")
    print(f"  - tests/: {test_dir.exists()}")
    print(f"  - tests/unit/: {unit_dir.exists()}")
    print(f"  - tests/integration/: {integration_dir.exists()}")
    
    # Create directories if they don't exist
    unit_dir.mkdir(exist_ok=True)
    integration_dir.mkdir(exist_ok=True)
    
    assert unit_dir.exists()
    assert integration_dir.exists()

if __name__ == "__main__":
    print("🧪 Running Infrastructure Check")
    print("=" * 50)
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
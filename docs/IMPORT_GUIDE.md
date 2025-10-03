# Bulk Import Documentation

## Overview

The GarageReg system supports bulk import of hierarchical data through CSV and XLSX files. The import system maintains the relational integrity of the Client → Site → Building → Gate hierarchy.

## Import Types

### 1. Hierarchical Import (`/api/v1/import/hierarchical`)

Imports the complete hierarchy in a single file. This is the most convenient option when you have all data in one place.

**Required columns:**
- `client_name`
- `site_name` 
- `building_name`
- `gate_name`

**Optional columns:**
- Client fields: `client_type`, `client_contact_person`, `client_email`, `client_phone`, `client_city`
- Site fields: `site_code`, `site_city`, `site_latitude`, `site_longitude`, `site_area_sqm`
- Building fields: `building_type`, `building_floors`, `building_units`, `building_year_built`
- Gate fields: `gate_type`, `manufacturer`, `model`, `serial_number`, `installation_date`, `width_cm`, `height_cm`, `weight_kg`, `material`, `max_cycles_per_day`, `current_cycle_count`, `status`

### 2. Entity-Specific Imports

Import specific entity types separately:

- **Clients only**: `/api/v1/import/clients`
- **Sites only**: `/api/v1/import/sites` (requires existing clients)
- **Buildings only**: `/api/v1/import/buildings` (requires existing sites)
- **Gates only**: `/api/v1/import/gates` (requires existing buildings)

## File Formats

### Supported Formats
- **CSV** (`.csv`) - UTF-8 encoding recommended
- **Excel** (`.xlsx`, `.xls`)

### File Requirements
- Maximum file size: 10MB
- UTF-8 encoding for CSV files (BOM supported)
- First row must contain column headers
- Column names are case-sensitive

## Data Validation

### Field Validation
- **Names**: 2-200 characters, required for all entities
- **Codes**: Optional, up to 50 characters
- **Types**: Must match predefined enums (see below)
- **Dates**: ISO format (YYYY-MM-DD) or Excel date format
- **Numbers**: Non-negative integers for dimensions, counts, etc.

### Enum Values

#### Client Types
- `residential` - Residential complexes
- `commercial` - Commercial buildings
- `industrial` - Industrial facilities  
- `mixed` - Mixed-use developments

#### Building Types
- `residential` - Residential buildings
- `office` - Office buildings
- `warehouse` - Warehouses
- `retail` - Retail spaces
- `mixed` - Mixed-use buildings
- `other` - Other building types

#### Gate Types
- `swing` - Swing gates
- `sliding` - Sliding gates
- `barrier` - Barrier gates
- `bollard` - Bollard systems
- `turnstile` - Turnstile gates

#### Gate Status
- `operational` - Fully operational (default)
- `maintenance` - Under maintenance
- `broken` - Broken/non-functional
- `decommissioned` - Decommissioned

## Import Behavior

### Duplicate Handling
- **Clients**: Matched by name within organization
- **Sites**: Matched by name within client
- **Buildings**: Matched by name within site
- **Gates**: Matched by name within building

If a duplicate is found, the existing entity is used rather than creating a new one.

### Relationship Creation
The import automatically creates the hierarchical relationships:
1. Client is created/found
2. Site is created/found and linked to client
3. Building is created/found and linked to site
4. Gate is created and linked to building

### Error Handling
- Invalid data skips the row and logs an error
- Missing required fields skip the row
- Invalid enum values skip the row
- Database constraint violations skip the row

## Sample Files

Sample files are provided in `/docs/samples/`:

1. **`hierarchical_sample.csv`** - Complete hierarchy example
2. **`clients_sample.csv`** - Client data only
3. **`sites_sample.csv`** - Site data with client references
4. **`buildings_sample.csv`** - Building data with site references
5. **`gates_sample.csv`** - Gate data with building references

## API Usage

### Authentication
All import endpoints require authentication and appropriate permissions:
- `MANAGE_CLIENTS` - For client imports
- `MANAGE_SITES` - For site imports
- `MANAGE_BUILDINGS` - For building imports
- `MANAGE_GATES` - For gate imports

### Import Response
```json
{
  "success": true,
  "total_rows": 100,
  "processed_rows": 95,
  "skipped_rows": 5,
  "errors": [
    "Row 15: Invalid gate_type 'unknown'",
    "Row 23: Missing required field 'client_name'"
  ],
  "warnings": [
    "Row 45: Gate 'Gate 1' already exists, skipping"
  ],
  "created_entities": {
    "clients": [1, 2, 3],
    "sites": [1, 2, 3, 4], 
    "buildings": [1, 2, 3, 4, 5],
    "gates": [1, 2, 3, 4, 5, 6]
  }
}
```

### Download Templates
Get CSV templates for any import type:
```
GET /api/v1/import/template/{import_type}
```

Where `import_type` is one of: `hierarchical`, `clients`, `sites`, `buildings`, `gates`

## Best Practices

### Data Preparation
1. **Validate data** before import using the templates
2. **Use consistent naming** across entities  
3. **Include optional fields** like codes for better organization
4. **Test with small files** first to validate format

### Performance
1. **Batch imports** - Large files are processed in batches
2. **Avoid duplicates** - Check existing data first
3. **Use hierarchical import** when possible for better performance

### Error Recovery
1. **Review error messages** for specific issues
2. **Fix data issues** and re-import failed rows
3. **Use entity-specific imports** to fill gaps

## Example Workflow

1. **Download template**: `GET /api/v1/import/template/hierarchical`
2. **Fill template** with your data
3. **Validate data** against requirements
4. **Import data**: `POST /api/v1/import/hierarchical` with file
5. **Review results** and fix any errors
6. **Re-import failed rows** if necessary

## Security Considerations

- Import operations are logged for audit trails
- Only users with appropriate permissions can import
- File size limits prevent abuse
- Data validation prevents malformed entries
- Organization isolation prevents cross-tenant data leaks

## Troubleshooting

### Common Issues
1. **File encoding**: Use UTF-8 for CSV files
2. **Column names**: Must match exactly (case-sensitive)
3. **Date formats**: Use YYYY-MM-DD format
4. **Missing entities**: Ensure parent entities exist for entity-specific imports
5. **Permission errors**: Verify user has required permissions

### Getting Help
- Check import response for specific error messages
- Review sample files for correct format
- Verify data against validation rules
- Contact support with specific error details
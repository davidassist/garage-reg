"""Dynamic checklist template service with EU standards preloading."""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.inspections import ChecklistTemplate, ChecklistItem
from app.models.auth import User
import json


class DynamicChecklistService:
    """Service for managing dynamic checklists with JSON schemas and EU standards."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template_from_schema(
        self, 
        schema: Dict[str, Any], 
        user: User,
        preload_standard: Optional[str] = None
    ) -> ChecklistTemplate:
        """Create a checklist template from a JSON schema."""
        
        # Create template
        template = ChecklistTemplate(
            org_id=user.org_id,
            name=schema.get("name", "Untitled Template"),
            description=schema.get("description", ""),
            category=schema.get("category", "general"),
            version=schema.get("version", "1.0"),
            template_type=schema.get("template_type", "general"),
            applicable_gate_types=schema.get("applicable_gate_types", []),
            applicable_manufacturers=schema.get("applicable_manufacturers", []),
            estimated_duration_minutes=schema.get("estimated_duration_minutes"),
            recommended_frequency_days=schema.get("recommended_frequency_days"),
            required_tools=schema.get("required_tools", []),
            required_skills=schema.get("required_skills", []),
            validation_schema=schema.get("validation_schema", {}),
            conditional_rules=schema.get("conditional_rules", {}),
            standards_references=schema.get("standards_references", {}),
            is_mandatory=schema.get("is_mandatory", False),
            settings=schema.get("settings", {})
        )
        
        self.db.add(template)
        self.db.flush()  # Get template ID
        
        # Create items from sections
        order_index = 0
        for section_data in schema.get("sections", []):
            section_name = section_data.get("name", "General")
            
            for item_data in section_data.get("items", []):
                item = self._create_checklist_item(
                    template.id, 
                    item_data, 
                    section_name, 
                    order_index,
                    user.org_id
                )
                self.db.add(item)
                order_index += 1
        
        # Apply preloaded standard if specified
        if preload_standard:
            self._apply_eu_standard(template, preload_standard)
        
        self.db.commit()
        return template
    
    def _create_checklist_item(
        self, 
        template_id: int, 
        item_data: Dict[str, Any], 
        section: str, 
        order_index: int,
        org_id: int
    ) -> ChecklistItem:
        """Create a single checklist item from schema data."""
        
        return ChecklistItem(
            org_id=org_id,
            template_id=template_id,
            title=item_data.get("title", "Untitled Item"),
            description=item_data.get("description"),
            instructions=item_data.get("instructions"),
            item_type=item_data.get("item_type", "bool"),
            measurement_type=item_data.get("measurement_type"),
            section=section,
            category=item_data.get("category"),
            order_index=order_index,
            is_required=item_data.get("is_required", True),
            is_recommended=item_data.get("is_recommended", False),
            requires_photo=item_data.get("requires_photo", False),
            requires_measurement=item_data.get("requires_measurement", False),
            requires_note=item_data.get("requires_note", False),
            validation_schema=item_data.get("validation_schema"),
            enum_options=item_data.get("enum_options"),
            measurement_unit=item_data.get("measurement_unit"),
            measurement_min=item_data.get("measurement_min"),
            measurement_max=item_data.get("measurement_max"),
            measurement_target=item_data.get("measurement_target"),
            measurement_tolerance=item_data.get("measurement_tolerance"),
            conditional_rules=item_data.get("conditional_rules"),
            pass_criteria=item_data.get("pass_criteria"),
            fail_criteria=item_data.get("fail_criteria"),
            safety_critical=item_data.get("safety_critical", False),
            severity_level=item_data.get("severity_level", "medium"),
            settings=item_data.get("settings", {})
        )
    
    def _apply_eu_standard(self, template: ChecklistTemplate, standard: str):
        """Apply EU standard references and additional validation rules."""
        
        standards_map = {
            "EN13241": {
                "full_name": "EN 13241-1:2003 - Industrial, commercial and garage doors and gates",
                "scope": "Safety in use of power operated doors and gates",
                "key_requirements": [
                    "Protection against crushing and shearing",
                    "Emergency release mechanisms",
                    "Safety devices and sensors",
                    "Manual operation capability"
                ]
            },
            "EN12453": {
                "full_name": "EN 12453:2017 - Industrial, commercial and garage doors and gates - Safety in use of power operated doors and gates - Requirements", 
                "scope": "Safety requirements for power operated doors and gates",
                "key_requirements": [
                    "Risk assessment and categorization",
                    "Safety device selection",
                    "Installation requirements",
                    "Testing and commissioning"
                ]
            },
            "EN12604": {
                "full_name": "EN 12604:2000 - Industrial, commercial and garage doors and gates - Mechanical aspects - Requirements",
                "scope": "Mechanical requirements and testing methods",
                "key_requirements": [
                    "Structural integrity",
                    "Operating forces",
                    "Endurance testing",
                    "Resistance to wind load"
                ]
            }
        }
        
        if standard in standards_map:
            standard_info = standards_map[standard]
            
            # Update template with standard reference
            current_refs = template.standards_references or {}
            current_refs[standard] = standard_info
            template.standards_references = current_refs
            
            # Add validation rules based on standard
            validation_schema = template.validation_schema or {}
            validation_schema["standard_compliance"] = {
                "type": "object",
                "properties": {
                    "applicable_standard": {"const": standard},
                    "compliance_verified": {"type": "boolean"},
                    "deviation_notes": {"type": "string"}
                },
                "required": ["applicable_standard", "compliance_verified"]
            }
            template.validation_schema = validation_schema
    
    def validate_inspection_data(
        self, 
        template_id: int, 
        inspection_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate inspection data against template schema and conditional rules."""
        
        template = self.db.query(ChecklistTemplate).filter(
            ChecklistTemplate.id == template_id
        ).first()
        
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "conditional_items": []
        }
        
        # Validate each item
        for item in template.items:
            item_key = f"item_{item.id}"
            item_value = inspection_data.get(item_key)
            
            # Check conditional logic
            if not self._should_item_be_active(item, inspection_data):
                validation_result["conditional_items"].append({
                    "item_id": item.id,
                    "title": item.title,
                    "status": "hidden"
                })
                continue
            
            # Validate required items
            if item.is_required and (item_value is None or item_value == ""):
                validation_result["is_valid"] = False
                validation_result["errors"].append({
                    "item_id": item.id,
                    "title": item.title,
                    "error": "Required item is missing"
                })
                continue
            
            # Validate measurement ranges
            if item.item_type == "number" and item_value is not None:
                try:
                    numeric_value = float(item_value)
                    
                    if item.measurement_min is not None and numeric_value < float(item.measurement_min):
                        validation_result["errors"].append({
                            "item_id": item.id,
                            "title": item.title,
                            "error": f"Value {numeric_value} is below minimum {item.measurement_min}"
                        })
                        validation_result["is_valid"] = False
                    
                    if item.measurement_max is not None and numeric_value > float(item.measurement_max):
                        validation_result["errors"].append({
                            "item_id": item.id,
                            "title": item.title,
                            "error": f"Value {numeric_value} is above maximum {item.measurement_max}"
                        })
                        validation_result["is_valid"] = False
                    
                    # Check tolerance warnings
                    if item.measurement_target is not None and item.measurement_tolerance is not None:
                        target = float(item.measurement_target)
                        tolerance = float(item.measurement_tolerance)
                        
                        if abs(numeric_value - target) > tolerance:
                            validation_result["warnings"].append({
                                "item_id": item.id,
                                "title": item.title,
                                "warning": f"Value {numeric_value} deviates from target {target} by more than tolerance {tolerance}"
                            })
                
                except ValueError:
                    validation_result["errors"].append({
                        "item_id": item.id,
                        "title": item.title,
                        "error": f"Invalid numeric value: {item_value}"
                    })
                    validation_result["is_valid"] = False
            
            # Validate enum options
            if item.item_type == "enum" and item.enum_options and item_value is not None:
                if item_value not in item.enum_options:
                    validation_result["errors"].append({
                        "item_id": item.id,
                        "title": item.title,
                        "error": f"Value '{item_value}' is not in allowed options: {item.enum_options}"
                    })
                    validation_result["is_valid"] = False
        
        return validation_result
    
    def _should_item_be_active(self, item: ChecklistItem, inspection_data: Dict[str, Any]) -> bool:
        """Check if an item should be active based on conditional rules."""
        
        if not item.conditional_rules:
            return True
        
        rules = item.conditional_rules
        condition_type = rules.get("condition", "always")
        
        if condition_type == "always":
            return True
        elif condition_type == "never":
            return False
        elif condition_type == "if":
            # Check if condition
            depends_on = rules.get("depends_on_item_id")
            if depends_on:
                parent_value = inspection_data.get(f"item_{depends_on}")
                expected_value = rules.get("expected_value")
                operator = rules.get("operator", "equals")
                
                if operator == "equals":
                    return parent_value == expected_value
                elif operator == "not_equals":
                    return parent_value != expected_value
                elif operator == "in":
                    return parent_value in expected_value if isinstance(expected_value, list) else False
                elif operator == "not_in":
                    return parent_value not in expected_value if isinstance(expected_value, list) else True
        
        return True
    
    def get_template_json_schema(self, template_id: int) -> Dict[str, Any]:
        """Generate a complete JSON schema for a template."""
        
        template = self.db.query(ChecklistTemplate).filter(
            ChecklistTemplate.id == template_id
        ).first()
        
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        schema = {
            "type": "object",
            "title": template.name,
            "description": template.description,
            "properties": {},
            "required": [],
            "sections": []
        }
        
        # Group items by section
        sections = {}
        for item in template.items:
            section_name = item.section or "General"
            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(item)
        
        # Build schema sections
        for section_name, items in sections.items():
            section_schema = {
                "name": section_name,
                "items": []
            }
            
            for item in items:
                item_schema = self._get_item_json_schema(item)
                section_schema["items"].append(item_schema)
                
                # Add to top-level schema
                item_key = f"item_{item.id}"
                schema["properties"][item_key] = item_schema.get("validation", {})
                
                if item.is_required:
                    schema["required"].append(item_key)
            
            schema["sections"].append(section_schema)
        
        return schema
    
    def _get_item_json_schema(self, item: ChecklistItem) -> Dict[str, Any]:
        """Generate JSON schema for a single checklist item."""
        
        item_schema = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "instructions": item.instructions,
            "item_type": item.item_type,
            "measurement_type": item.measurement_type,
            "section": item.section,
            "order_index": item.order_index,
            "is_required": item.is_required,
            "is_recommended": item.is_recommended,
            "safety_critical": item.safety_critical,
            "severity_level": item.severity_level,
            "validation": {}
        }
        
        # Build validation schema based on item type
        if item.item_type == "bool":
            item_schema["validation"] = {"type": "boolean"}
        
        elif item.item_type == "enum":
            item_schema["validation"] = {
                "type": "string",
                "enum": item.enum_options or []
            }
            item_schema["enum_options"] = item.enum_options
        
        elif item.item_type == "number":
            validation = {"type": "number"}
            if item.measurement_min is not None:
                validation["minimum"] = float(item.measurement_min)
            if item.measurement_max is not None:
                validation["maximum"] = float(item.measurement_max)
            
            item_schema["validation"] = validation
            item_schema["measurement_unit"] = item.measurement_unit
            item_schema["measurement_target"] = float(item.measurement_target) if item.measurement_target else None
            item_schema["measurement_tolerance"] = float(item.measurement_tolerance) if item.measurement_tolerance else None
        
        elif item.item_type in ["photo", "note", "text"]:
            item_schema["validation"] = {"type": "string"}
        
        # Add conditional logic
        if item.conditional_rules:
            item_schema["conditional_rules"] = item.conditional_rules
        
        # Add custom validation schema if present
        if item.validation_schema:
            item_schema["validation"].update(item.validation_schema)
        
        return item_schema
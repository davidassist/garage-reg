"""EU Standards preloaded checklist templates."""

from typing import Dict, Any

class EUStandardTemplates:
    """Predefined checklist templates based on EU standards."""
    
    @staticmethod
    def get_en13241_template() -> Dict[str, Any]:
        """EN 13241-1:2003 - Industrial, commercial and garage doors and gates template."""
        
        return {
            "name": "EN 13241-1:2003 Gate Safety Inspection",
            "description": "Safety inspection checklist based on EN 13241-1:2003 standard for industrial, commercial and garage doors and gates",
            "category": "safety",
            "version": "1.0",
            "template_type": "standard_based",
            "applicable_gate_types": ["automatic", "electric", "industrial"],
            "estimated_duration_minutes": 90,
            "recommended_frequency_days": 90,  # Quarterly
            "required_tools": ["force_gauge", "measuring_tape", "multimeter", "safety_equipment"],
            "required_skills": ["electrical_safety", "mechanical_inspection", "risk_assessment"],
            "standards_references": {
                "EN13241": {
                    "clause_references": ["4.2", "4.3", "5.1", "5.2", "6.1"],
                    "safety_categories": ["Category 1", "Category 2", "Category 3", "Category 4"]
                }
            },
            "validation_schema": {
                "type": "object",
                "properties": {
                    "inspection_environment": {
                        "type": "object",
                        "properties": {
                            "weather_suitable": {"type": "boolean"},
                            "visibility_adequate": {"type": "boolean"}
                        }
                    }
                }
            },
            "sections": [
                {
                    "name": "Pre-Inspection Safety Check",
                    "items": [
                        {
                            "title": "Power supply disconnected for testing",
                            "description": "Ensure safe isolation before inspection",
                            "item_type": "bool",
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "critical",
                            "instructions": "Switch off main power and verify with suitable test equipment"
                        },
                        {
                            "title": "Warning signs and barriers in place",
                            "description": "Area secured for safe inspection",
                            "item_type": "bool", 
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "high"
                        }
                    ]
                },
                {
                    "name": "Visual Safety Inspection",
                    "items": [
                        {
                            "title": "Gate structure condition",
                            "description": "Overall structural integrity assessment",
                            "item_type": "enum",
                            "enum_options": ["excellent", "good", "fair", "poor", "unsafe"],
                            "is_required": True,
                            "severity_level": "high",
                            "pass_criteria": "No visible damage, corrosion within acceptable limits",
                            "fail_criteria": "Structural damage, excessive corrosion, loose components"
                        },
                        {
                            "title": "Safety device presence verification",
                            "description": "Check all required safety devices are present",
                            "item_type": "bool",
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "critical",
                            "instructions": "Verify presence of: safety edges, photocells, emergency stop, manual release"
                        },
                        {
                            "title": "Emergency release mechanism accessibility",
                            "description": "Manual release mechanism easily accessible",
                            "item_type": "bool",
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "high",
                            "pass_criteria": "Release clearly marked, accessible, operates smoothly"
                        },
                        {
                            "title": "Warning labels and signage",
                            "description": "All required warning labels present and legible",
                            "item_type": "enum",
                            "enum_options": ["all_present", "some_missing", "illegible", "none_present"],
                            "is_required": True,
                            "severity_level": "medium"
                        }
                    ]
                },
                {
                    "name": "Force and Speed Measurements",
                    "items": [
                        {
                            "title": "Closing force measurement",
                            "description": "Force exerted during closing motion (EN 12453)",
                            "item_type": "number",
                            "measurement_type": "numeric_range",
                            "measurement_unit": "N",
                            "measurement_max": 400,
                            "measurement_target": 150,
                            "measurement_tolerance": 50,
                            "is_required": True,
                            "requires_measurement": True,
                            "safety_critical": True,
                            "severity_level": "critical",
                            "instructions": "Measure at leading edge using calibrated force gauge"
                        },
                        {
                            "title": "Opening speed",
                            "description": "Gate opening speed measurement",
                            "item_type": "number", 
                            "measurement_type": "numeric_range",
                            "measurement_unit": "m/s",
                            "measurement_min": 0.1,
                            "measurement_max": 0.5,
                            "measurement_target": 0.3,
                            "measurement_tolerance": 0.1,
                            "is_required": True,
                            "requires_measurement": True,
                            "severity_level": "medium"
                        },
                        {
                            "title": "Closing speed",
                            "description": "Gate closing speed measurement", 
                            "item_type": "number",
                            "measurement_type": "numeric_range",
                            "measurement_unit": "m/s",
                            "measurement_min": 0.1,
                            "measurement_max": 0.5,
                            "measurement_target": 0.25,
                            "measurement_tolerance": 0.1,
                            "is_required": True,
                            "requires_measurement": True,
                            "severity_level": "medium"
                        }
                    ]
                },
                {
                    "name": "Safety Device Testing",
                    "items": [
                        {
                            "title": "Safety edge/strip function test",
                            "description": "Test safety edge stops and reverses gate motion",
                            "item_type": "enum",
                            "enum_options": ["pass", "fail", "not_applicable"],
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "critical",
                            "conditional_rules": {
                                "condition": "if",
                                "depends_on_feature": "safety_edge_present",
                                "expected_value": True
                            }
                        },
                        {
                            "title": "Photocell/light curtain test",
                            "description": "Test infrared safety devices stop gate motion",
                            "item_type": "enum",
                            "enum_options": ["pass", "fail", "not_applicable"],
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "critical",
                            "instructions": "Block beam during gate operation, verify immediate stop"
                        },
                        {
                            "title": "Emergency stop function",
                            "description": "Emergency stop button immediately halts all motion",
                            "item_type": "bool",
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "critical"
                        },
                        {
                            "title": "Manual release operation test",
                            "description": "Manual release allows gate to be moved by hand",
                            "item_type": "bool",
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "high",
                            "instructions": "Activate manual release, verify gate can be moved with ≤225N force"
                        }
                    ]
                },
                {
                    "name": "Risk Assessment Notes",
                    "items": [
                        {
                            "title": "Risk category assessment",
                            "description": "Determine appropriate safety category per EN 12453",
                            "item_type": "enum",
                            "enum_options": ["Category_1", "Category_2", "Category_3", "Category_4"],
                            "is_required": True,
                            "severity_level": "high",
                            "instructions": "Consider usage frequency, user type, and environmental factors"
                        },
                        {
                            "title": "Additional safety recommendations",
                            "description": "Notes on recommended safety improvements",
                            "item_type": "note",
                            "is_required": False,
                            "is_recommended": True,
                            "requires_note": True
                        },
                        {
                            "title": "Inspection photos",
                            "description": "Photographic evidence of safety devices and overall condition",
                            "item_type": "photo",
                            "is_required": False,
                            "is_recommended": True,
                            "requires_photo": True
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_en12453_template() -> Dict[str, Any]:
        """EN 12453:2017 - Safety in use of power operated doors and gates."""
        
        return {
            "name": "EN 12453:2017 Power Gate Safety Assessment",
            "description": "Comprehensive safety assessment for power operated gates per EN 12453:2017",
            "category": "safety",
            "version": "1.0", 
            "template_type": "standard_based",
            "applicable_gate_types": ["automatic", "electric"],
            "estimated_duration_minutes": 120,
            "recommended_frequency_days": 365,  # Annual
            "required_tools": ["force_gauge", "timer", "measuring_equipment", "electrical_tester"],
            "required_skills": ["risk_assessment", "electrical_safety", "safety_device_testing"],
            "standards_references": {
                "EN12453": {
                    "tables_referenced": ["Table 1", "Table 2", "Table 3"], 
                    "annexes": ["Annex A", "Annex B"]
                }
            },
            "sections": [
                {
                    "name": "Usage Assessment",
                    "items": [
                        {
                            "title": "Type of use",
                            "description": "Determine gate usage category",
                            "item_type": "enum",
                            "enum_options": ["residential", "commercial", "industrial", "public"],
                            "is_required": True,
                            "severity_level": "high"
                        },
                        {
                            "title": "User type",
                            "description": "Category of persons using the gate",
                            "item_type": "enum",
                            "enum_options": ["informed_persons", "instructed_persons", "public"],
                            "is_required": True,
                            "severity_level": "high"
                        },
                        {
                            "title": "Frequency of use",
                            "description": "Daily usage frequency category",
                            "item_type": "enum",
                            "enum_options": ["intensive", "normal", "reduced"],
                            "is_required": True,
                            "severity_level": "medium"
                        }
                    ]
                },
                {
                    "name": "Safety Device Selection Verification",
                    "items": [
                        {
                            "title": "Appropriate safety devices installed",
                            "description": "Verify correct safety devices per Table 1 of EN 12453",
                            "item_type": "bool",
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "critical",
                            "instructions": "Check against EN 12453 Table 1 for required devices"
                        },
                        {
                            "title": "Safety device positioning correct",
                            "description": "Safety devices positioned according to standard requirements",
                            "item_type": "bool",
                            "is_required": True,
                            "safety_critical": True,
                            "severity_level": "high"
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_en12604_template() -> Dict[str, Any]:
        """EN 12604:2000 - Mechanical aspects requirements."""
        
        return {
            "name": "EN 12604:2000 Mechanical Requirements Check",
            "description": "Mechanical integrity and performance testing per EN 12604:2000",
            "category": "mechanical",
            "version": "1.0",
            "template_type": "standard_based", 
            "applicable_gate_types": ["automatic", "manual", "industrial"],
            "estimated_duration_minutes": 180,
            "recommended_frequency_days": 365,  # Annual
            "required_tools": ["force_gauge", "measuring_tape", "load_testing_equipment", "endurance_test_tools"],
            "required_skills": ["mechanical_testing", "structural_assessment", "load_calculations"],
            "standards_references": {
                "EN12604": {
                    "test_methods": ["5.2", "5.3", "5.4", "5.5"],
                    "performance_criteria": ["Table 2", "Table 3"]
                }
            },
            "sections": [
                {
                    "name": "Structural Integrity",
                    "items": [
                        {
                            "title": "Static load test",
                            "description": "Gate withstands static loads per standard",
                            "item_type": "enum",
                            "enum_options": ["pass", "fail", "not_tested"],
                            "is_required": True,
                            "severity_level": "critical",
                            "instructions": "Apply test loads per EN 12604 clause 5.2"
                        },
                        {
                            "title": "Wind load resistance",
                            "description": "Gate designed for specified wind loads",
                            "item_type": "number",
                            "measurement_unit": "Pa",
                            "measurement_min": 500,
                            "measurement_target": 1000,
                            "is_required": True,
                            "requires_measurement": True,
                            "severity_level": "high"
                        }
                    ]
                },
                {
                    "name": "Operating Forces",
                    "items": [
                        {
                            "title": "Manual operating force",
                            "description": "Force required to manually operate gate",
                            "item_type": "number",
                            "measurement_unit": "N", 
                            "measurement_max": 225,
                            "measurement_target": 150,
                            "measurement_tolerance": 25,
                            "is_required": True,
                            "requires_measurement": True,
                            "severity_level": "medium"
                        }
                    ]
                },
                {
                    "name": "Endurance Testing",
                    "items": [
                        {
                            "title": "Cycle count since last test",
                            "description": "Number of operating cycles since last endurance assessment",
                            "item_type": "number",
                            "measurement_unit": "cycles",
                            "is_required": True,
                            "requires_measurement": True,
                            "severity_level": "medium"
                        },
                        {
                            "title": "Endurance test required",
                            "description": "Based on cycle count, endurance test needed",
                            "item_type": "bool",
                            "conditional_rules": {
                                "condition": "if",
                                "depends_on": "cycle_count",
                                "operator": "greater_than", 
                                "expected_value": 25000
                            }
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """Get all predefined EU standard templates."""
        
        return {
            "EN13241": EUStandardTemplates.get_en13241_template(),
            "EN12453": EUStandardTemplates.get_en12453_template(),
            "EN12604": EUStandardTemplates.get_en12604_template()
        }
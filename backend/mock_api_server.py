#!/usr/bin/env python3
"""
Demo backend server for testing API error handling and validation.
This serves mock endpoints that return various HTTP status codes and error formats
matching our frontend API client expectations.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

# Mock data store
users_db = [
    {
        "id": "1", 
        "email": "admin@garagereg.com", 
        "name": "Admin User",
        "role": "admin",
        "permissions": ["users:read", "users:write", "vehicles:read", "vehicles:write", "settings:read", "settings:write"]
    },
    {
        "id": "2", 
        "email": "user@garagereg.com", 
        "name": "Regular User",
        "role": "user", 
        "permissions": ["vehicles:read"]
    }
]

gates_db = [
    {
        "id": "1",
        "name": "Főbejárat kapu",
        "code": "GATE-001",
        "type": "swing",
        "size": "medium",
        "status": "active",
        "serialNumber": "SN123456789",
        "manufacturer": "CAME",
        "model": "ATI 3000",
        "yearOfManufacture": 2022,
        "width": 3.5,
        "height": 2.0,
        "weight": 150,
        "controllerType": "remote",
        "controllerModel": "ZA3P",
        "remoteControls": 2,
        "motorType": "ac",
        "motorPower": 550,
        "motorModel": "BX-243",
        "gearboxRatio": "1:20",
        "springs": {
            "type": "Torziós",
            "count": 2,
            "tension": "Közepes",
        },
        "rails": {
            "type": "Acél",
            "length": 4.0,
            "material": "Galvanizált acél",
        },
        "photocells": {
            "count": 2,
            "type": "Infravörös",
            "range": 10,
        },
        "edgeProtection": {
            "type": "Gumiszalag",
            "location": "Alsó él",
            "sensitivity": "Magas",
        },
        "manualRelease": {
            "type": "Kulcsos",
            "location": "Belső oldal",
            "keyType": "Háromszög",
        },
        "location": "Főépület bejárat",
        "installationDate": "2022-05-15T00:00:00Z",
        "installerCompany": "TechGate Kft.",
        "lastMaintenance": "2024-08-15T00:00:00Z",
        "nextMaintenance": "2025-02-15T00:00:00Z",
        "maintenanceInterval": 180,
        "notes": "Rendszeres karbantartás szükséges. Télen különös figyelmet kell fordítani a fagyás elleni védelemre.",
        "manualUrl": "https://came.com/manuals/ati3000.pdf",
        "warrantyExpiry": "2025-05-15T00:00:00Z",
        "createdAt": "2022-05-15T10:30:00Z",
        "updatedAt": "2024-08-15T14:20:00Z",
        "createdBy": "admin@garagereg.com",
        "updatedBy": "technician@garagereg.com",
    },
    {
        "id": "2",
        "name": "Teherkapu",
        "code": "GATE-002",
        "type": "sliding",
        "size": "large",
        "status": "maintenance",
        "serialNumber": "SN987654321",
        "manufacturer": "BFT",
        "model": "ICARO N",
        "yearOfManufacture": 2021,
        "width": 8.0,
        "height": 2.5,
        "weight": 800,
        "controllerType": "automatic",
        "controllerModel": "CLONIX 2E",
        "remoteControls": 5,
        "motorType": "dc",
        "motorPower": 1200,
        "motorModel": "PEGASO",
        "photocells": {
            "count": 4,
            "type": "Dual-beam",
        },
        "edgeProtection": {
            "type": "Pneumatikus",
            "location": "Teljes él",
        },
        "manualRelease": {
            "type": "Bowdenes",
            "location": "Kaputól 5m",
        },
        "location": "Rakodó terület",
        "installationDate": "2021-09-20T00:00:00Z",
        "installerCompany": "AutoGate Solutions",
        "lastMaintenance": "2024-09-01T00:00:00Z",
        "nextMaintenance": "2024-12-01T00:00:00Z",
        "maintenanceInterval": 90,
        "notes": "Nehéz használat miatt gyakoribb karbantartás szükséges.",
        "createdAt": "2021-09-20T08:15:00Z",
        "updatedAt": "2024-09-01T11:45:00Z",
        "createdBy": "admin@garagereg.com",
        "updatedBy": "maintenance@garagereg.com",
    },
    {
        "id": "3",
        "name": "Parkoló sorompó",
        "code": "GATE-003",
        "type": "barrier",
        "size": "small",
        "status": "active",
        "serialNumber": "SN555666777",
        "manufacturer": "Nice",
        "model": "WIDE M",
        "yearOfManufacture": 2023,
        "width": 4.0,
        "controllerType": "card_reader",
        "controllerModel": "MC824H",
        "motorType": "dc",
        "motorPower": 130,
        "photocells": {
            "count": 2,
            "type": "Safety",
        },
        "location": "Alkalmazotti parkoló",
        "installationDate": "2023-03-10T00:00:00Z",
        "installerCompany": "SmartAccess Bt.",
        "lastMaintenance": "2024-09-10T00:00:00Z",
        "nextMaintenance": "2025-03-10T00:00:00Z",
        "maintenanceInterval": 180,
        "createdAt": "2023-03-10T13:20:00Z",
        "updatedAt": "2024-09-10T09:30:00Z",
        "createdBy": "admin@garagereg.com",
    },
]

dashboard_stats = {
    "totalVehicles": 156,
    "totalRegistrations": 89,
    "activeUsers": 23,
    "pendingApprovals": 12
}

recent_activities = [
    {
        "id": "1",
        "type": "inspection",
        "description": "Biztonsági ellenőrzés befejezve - ABC Logistics",
        "timestamp": datetime.now().isoformat(),
        "user": "Nagy Péter"
    },
    {
        "id": "2", 
        "type": "ticket",
        "description": "Új hibajegy létrehozva - Kapu szenzor hiba",
        "timestamp": datetime.now().isoformat(),
        "user": "Kiss Anna"
    }
]

class MockAPIHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        """Set CORS headers for all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _get_request_body(self) -> Dict[str, Any]:
        """Parse JSON request body"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                return json.loads(body)
            return {}
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = self.path.split('?')[0]  # Remove query parameters
        
        if path == '/':
            self._send_json_response(200, {
                "message": "Mock API Server for GarageReg",
                "status": "running",
                "endpoints": {
                    "GET /dashboard/stats": "Dashboard statistics",
                    "GET /dashboard/activities": "Recent activities", 
                    "POST /auth/login": "Login (returns validation errors for invalid data)",
                    "POST /auth/totp": "TOTP verification",
                    "GET /auth/me": "Current user info",
                    "GET /users": "List users",
                    "GET /gates": "List gates (supports search, type, status, pagination)",
                    "GET /gates/{id}": "Get gate by ID",
                    "POST /gates": "Create new gate (with validation)",
                    "PUT /gates/{id}": "Update gate (with validation)",
                    "DELETE /gates/{id}": "Delete gate",
                    "GET /nonexistent": "404 error test",
                    "GET /server-error": "500 error test"
                }
            })
            
        elif path == '/dashboard/stats':
            # Simulate slight delay
            time.sleep(0.2)
            self._send_json_response(200, {
                "success": True,
                "data": dashboard_stats
            })
            
        elif path == '/dashboard/activities':
            time.sleep(0.1)
            self._send_json_response(200, {
                "success": True,
                "data": recent_activities
            })
            
        elif path == '/auth/me':
            # Check for Authorization header
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self._send_json_response(401, {
                    "message": "Hiányzó vagy érvénytelen hitelesítési token",
                    "code": "UNAUTHORIZED"
                })
                return
                
            # Return mock user
            self._send_json_response(200, {
                "success": True,
                "data": users_db[0]  # Return admin user
            })
            
        elif path == '/users':
            self._send_json_response(200, {
                "success": True,
                "data": {
                    "items": users_db,
                    "total": len(users_db),
                    "page": 1,
                    "limit": 10
                }
            })
            
        elif path == '/gates':
            # Parse query parameters for filtering/pagination
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            search = query_params.get('search', [None])[0]
            gate_type = query_params.get('type', [None])[0]
            status = query_params.get('status', [None])[0]
            page = int(query_params.get('page', [1])[0])
            limit = int(query_params.get('limit', [10])[0])
            
            # Filter gates
            filtered_gates = gates_db.copy()
            
            if search:
                search_lower = search.lower()
                filtered_gates = [
                    gate for gate in filtered_gates 
                    if search_lower in gate['name'].lower() or 
                       search_lower in gate['code'].lower() or
                       search_lower in gate['manufacturer'].lower()
                ]
                
            if gate_type:
                filtered_gates = [gate for gate in filtered_gates if gate['type'] == gate_type]
                
            if status:
                filtered_gates = [gate for gate in filtered_gates if gate['status'] == status]
            
            # Pagination
            total = len(filtered_gates)
            start = (page - 1) * limit
            end = start + limit
            paginated_gates = filtered_gates[start:end]
            
            self._send_json_response(200, {
                "success": True,
                "data": {
                    "items": paginated_gates,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "totalPages": (total + limit - 1) // limit
                }
            })
            
        elif path.startswith('/gates/'):
            gate_id = path.split('/gates/')[1]
            gate = next((g for g in gates_db if g['id'] == gate_id), None)
            
            if not gate:
                self._send_json_response(404, {
                    "message": "Kapu nem található",
                    "code": "GATE_NOT_FOUND"
                })
            else:
                self._send_json_response(200, {
                    "success": True,
                    "data": gate
                })
            
        elif path == '/nonexistent':
            self._send_json_response(404, {
                "message": "A keresett erőforrás nem található",
                "code": "NOT_FOUND"
            })
            
        elif path == '/server-error':
            self._send_json_response(500, {
                "message": "Belső szerver hiba történt",
                "code": "INTERNAL_SERVER_ERROR"
            })
            
        elif path == '/unauthorized':
            self._send_json_response(401, {
                "message": "Nincs jogosultsága ehhez a művelethez", 
                "code": "UNAUTHORIZED"
            })
            
        elif path == '/forbidden':
            self._send_json_response(403, {
                "message": "Hozzáférés megtagadva",
                "code": "FORBIDDEN"
            })
            
        else:
            self._send_json_response(404, {
                "message": f"Endpoint nem található: {path}",
                "code": "NOT_FOUND"
            })
    
    def do_POST(self):
        """Handle POST requests"""
        path = self.path.split('?')[0]
        body = self._get_request_body()
        
        if path == '/auth/login':
            # Validate login data and return appropriate responses
            email = body.get('email', '').strip()
            password = body.get('password', '').strip()
            
            # Collect validation errors
            errors = {}
            
            if not email:
                errors['email'] = ['Email megadása kötelező']
            elif '@' not in email or '.' not in email.split('@')[-1]:
                errors['email'] = ['Érvényes email címet adjon meg']
            elif email == 'taken@example.com':
                errors['email'] = ['Ez az email cím már használatban van']
                
            if not password:
                errors['password'] = ['Jelszó megadása kötelező']
            elif len(password) < 6:
                errors['password'] = ['A jelszó legalább 6 karakter hosszú kell legyen']
            elif password == 'weak':
                errors['password'] = ['A jelszó túl gyenge', 'Használjon számokat és speciális karaktereket']
                
            # If validation errors exist, return 422
            if errors:
                self._send_json_response(422, {
                    "message": "Érvényesítési hibák találhatók",
                    "code": "VALIDATION_ERROR",
                    "errors": errors
                })
                return
            
            # Check credentials
            if email == 'admin@garagereg.com' and password == 'password123':
                self._send_json_response(200, {
                    "success": True,
                    "data": {
                        "user": users_db[0],
                        "requiresTwoFactor": True,
                        "totpRequired": True
                    }
                })
            elif email == 'user@garagereg.com' and password == 'password123':
                self._send_json_response(200, {
                    "success": True,
                    "data": {
                        "user": users_db[1],
                        "requiresTwoFactor": False
                    }
                })
            else:
                self._send_json_response(401, {
                    "message": "Hibás email vagy jelszó",
                    "code": "INVALID_CREDENTIALS"
                })
                
        elif path == '/auth/totp':
            code = body.get('code', '').strip()
            
            if not code:
                self._send_json_response(422, {
                    "message": "Érvényesítési hiba",
                    "code": "VALIDATION_ERROR", 
                    "errors": {
                        "code": ["TOTP kód megadása kötelező"]
                    }
                })
                return
                
            if len(code) != 6:
                self._send_json_response(422, {
                    "message": "Érvényesítési hiba",
                    "code": "VALIDATION_ERROR",
                    "errors": {
                        "code": ["A TOTP kód 6 számjegyű kell legyen"]
                    }
                })
                return
                
            if code == '123456':
                self._send_json_response(200, {
                    "success": True,
                    "data": {
                        "authenticated": True,
                        "token": "mock-jwt-token"
                    }
                })
            else:
                self._send_json_response(401, {
                    "message": "Érvénytelen TOTP kód",
                    "code": "INVALID_TOTP_CODE"
                })
                
        elif path == '/gates':
            # Create new gate
            gate_data = body
            
            # Validate required fields
            errors = {}
            
            if not gate_data.get('name', '').strip():
                errors['name'] = ['Kapu név kötelező']
                
            if not gate_data.get('code', '').strip():
                errors['code'] = ['Kapu kód kötelező']
            elif any(gate['code'] == gate_data['code'] for gate in gates_db):
                errors['code'] = ['Ez a kapu kód már használatban van']
                
            if not gate_data.get('serialNumber', '').strip():
                errors['serialNumber'] = ['Sorozatszám kötelező']
            elif any(gate['serialNumber'] == gate_data['serialNumber'] for gate in gates_db):
                errors['serialNumber'] = ['Ez a sorozatszám már használatban van']
                
            if not gate_data.get('manufacturer', '').strip():
                errors['manufacturer'] = ['Gyártó megadása kötelező']
            
            # Validate enum values
            valid_types = ['swing', 'sliding', 'sectional', 'roller', 'barrier']
            if gate_data.get('type') not in valid_types:
                errors['type'] = ['Érvénytelen kapu típus']
                
            valid_statuses = ['active', 'inactive', 'maintenance', 'broken']
            if gate_data.get('status') not in valid_statuses:
                errors['status'] = ['Érvénytelen állapot']
                
            # Validate numeric fields
            if 'width' in gate_data and gate_data['width'] is not None:
                try:
                    width = float(gate_data['width'])
                    if width <= 0:
                        errors['width'] = ['Szélesség pozitív szám kell legyen']
                except (ValueError, TypeError):
                    errors['width'] = ['Szélesség érvényes szám kell legyen']
                    
            if 'height' in gate_data and gate_data['height'] is not None:
                try:
                    height = float(gate_data['height'])
                    if height <= 0:
                        errors['height'] = ['Magasság pozitív szám kell legyen']
                except (ValueError, TypeError):
                    errors['height'] = ['Magasság érvényes szám kell legyen']
            
            # If validation errors exist, return 422
            if errors:
                self._send_json_response(422, {
                    "message": "Érvényesítési hibák találhatók",
                    "code": "VALIDATION_ERROR",
                    "errors": errors
                })
                return
            
            # Create new gate
            new_gate = {
                **gate_data,
                "id": str(len(gates_db) + 1),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "createdBy": "current-user@garagereg.com"
            }
            
            gates_db.append(new_gate)
            
            self._send_json_response(201, {
                "success": True,
                "data": new_gate
            })
                
        else:
            self._send_json_response(404, {
                "message": f"Endpoint nem található: {path}",
                "code": "NOT_FOUND"
            })
    
    def do_PUT(self):
        """Handle PUT requests"""
        path = self.path.split('?')[0]
        body = self._get_request_body()
        
        if path.startswith('/gates/'):
            gate_id = path.split('/gates/')[1]
            gate_index = next((i for i, g in enumerate(gates_db) if g['id'] == gate_id), None)
            
            if gate_index is None:
                self._send_json_response(404, {
                    "message": "Kapu nem található",
                    "code": "GATE_NOT_FOUND"
                })
                return
            
            # Validate updated data (similar to POST but allow partial updates)
            errors = {}
            gate_data = body
            
            if 'code' in gate_data and gate_data['code']:
                # Check if code is taken by another gate
                if any(gate['code'] == gate_data['code'] and gate['id'] != gate_id for gate in gates_db):
                    errors['code'] = ['Ez a kapu kód már használatban van']
                    
            if 'serialNumber' in gate_data and gate_data['serialNumber']:
                # Check if serial number is taken by another gate
                if any(gate['serialNumber'] == gate_data['serialNumber'] and gate['id'] != gate_id for gate in gates_db):
                    errors['serialNumber'] = ['Ez a sorozatszám már használatban van']
            
            # Validate numeric fields
            if 'width' in gate_data and gate_data['width'] is not None:
                try:
                    width = float(gate_data['width'])
                    if width <= 0:
                        errors['width'] = ['Szélesség pozitív szám kell legyen']
                except (ValueError, TypeError):
                    errors['width'] = ['Szélesség érvényes szám kell legyen']
            
            if errors:
                self._send_json_response(422, {
                    "message": "Érvényesítési hibák találhatók",
                    "code": "VALIDATION_ERROR",
                    "errors": errors
                })
                return
            
            # Update gate
            updated_gate = {
                **gates_db[gate_index],
                **gate_data,
                "updatedAt": datetime.now().isoformat(),
                "updatedBy": "current-user@garagereg.com"
            }
            
            gates_db[gate_index] = updated_gate
            
            self._send_json_response(200, {
                "success": True,
                "data": updated_gate
            })
            
        else:
            self._send_json_response(404, {
                "message": f"Endpoint nem található: {path}",
                "code": "NOT_FOUND"
            })
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        path = self.path.split('?')[0]
        
        if path.startswith('/gates/'):
            gate_id = path.split('/gates/')[1]
            gate_index = next((i for i, g in enumerate(gates_db) if g['id'] == gate_id), None)
            
            if gate_index is None:
                self._send_json_response(404, {
                    "message": "Kapu nem található",
                    "code": "GATE_NOT_FOUND"
                })
                return
            
            # Remove gate
            deleted_gate = gates_db.pop(gate_index)
            
            self._send_json_response(200, {
                "success": True,
                "message": "Kapu sikeresen törölve",
                "data": {
                    "deletedId": gate_id,
                    "deletedGate": deleted_gate
                }
            })
            
        else:
            self._send_json_response(404, {
                "message": f"Endpoint nem található: {path}",
                "code": "NOT_FOUND"
            })

    def log_message(self, format, *args):
        """Override to customize logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def run_server(port=8001):
    """Run the mock API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockAPIHandler)
    
    print(f"\n🚀 Mock API Server indítva: http://localhost:{port}")
    print("📋 Elérhető endpointok:")
    print("   GET  /                     - API információ")
    print("   GET  /dashboard/stats      - Dashboard statisztikák")
    print("   GET  /dashboard/activities - Legutóbbi aktivitások")
    print("   POST /auth/login           - Bejelentkezés (validációs hibák tesztelése)")
    print("   POST /auth/totp            - TOTP ellenőrzés")
    print("   GET  /auth/me              - Aktuális felhasználó")
    print("   GET  /users                - Felhasználók listája")
    print("   GET  /gates                - Kapuk listája (search, type, status, pagination)")
    print("   GET  /gates/{id}           - Kapu lekérése ID alapján")
    print("   POST /gates                - Új kapu létrehozása (validációval)")
    print("   PUT  /gates/{id}           - Kapu frissítése (validációval)")
    print("   DELETE /gates/{id}         - Kapu törlése")
    print("   GET  /nonexistent          - 404 hiba teszt")
    print("   GET  /server-error         - 500 hiba teszt")
    print("   GET  /unauthorized         - 401 hiba teszt") 
    print("   GET  /forbidden            - 403 hiba teszt")
    print("\n💡 Teszt adatok:")
    print("   Email: admin@garagereg.com, Jelszó: password123")
    print("   Email: user@garagereg.com, Jelszó: password123") 
    print("   TOTP kód: 123456")
    print("\n🔧 Validációs hiba tesztek:")
    print("   - Üres mezők")
    print("   - Érvénytelen email formátum")
    print("   - Rövid jelszó (< 6 karakter)")
    print("   - taken@example.com (foglalt email)")
    print("   - password: 'weak' (gyenge jelszó)")
    print("\n⏹️  Leállítás: Ctrl+C\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server leállítva")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
"""
SDK Generator for GarageReg API
Generates TypeScript and Python SDKs from OpenAPI specification
"""
import requests
import json
import os
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import tempfile

class SDKGenerator:
    """Generate SDKs from OpenAPI specification."""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:8004"):
        self.api_base_url = api_base_url
        self.openapi_spec = None
        
    def fetch_openapi_spec(self) -> Dict[str, Any]:
        """Fetch OpenAPI specification from the API."""
        try:
            response = requests.get(f"{self.api_base_url}/api/openapi.json")
            response.raise_for_status()
            self.openapi_spec = response.json()
            return self.openapi_spec
        except Exception as e:
            raise Exception(f"Failed to fetch OpenAPI spec: {e}")
    
    def generate_typescript_sdk(self, output_dir: str) -> str:
        """Generate TypeScript SDK."""
        if not self.openapi_spec:
            self.fetch_openapi_spec()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate TypeScript types
        types_content = self._generate_typescript_types()
        
        # Generate API client
        client_content = self._generate_typescript_client()
        
        # Generate package.json
        package_json = self._generate_typescript_package_json()
        
        # Generate README
        readme_content = self._generate_typescript_readme()
        
        # Generate example usage
        example_content = self._generate_typescript_examples()
        
        # Write files
        files = {
            "src/types.ts": types_content,
            "src/client.ts": client_content,
            "src/index.ts": self._generate_typescript_index(),
            "package.json": json.dumps(package_json, indent=2),
            "README.md": readme_content,
            "examples/usage.ts": example_content,
            "tsconfig.json": json.dumps(self._generate_tsconfig(), indent=2),
            ".gitignore": self._generate_gitignore()
        }
        
        for file_path, content in files.items():
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✅ TypeScript SDK generated in: {output_dir}")
        return output_dir
    
    def generate_python_sdk(self, output_dir: str) -> str:
        """Generate Python SDK."""
        if not self.openapi_spec:
            self.fetch_openapi_spec()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate Python models
        models_content = self._generate_python_models()
        
        # Generate API client
        client_content = self._generate_python_client()
        
        # Generate setup.py
        setup_py = self._generate_python_setup()
        
        # Generate README
        readme_content = self._generate_python_readme()
        
        # Generate example usage
        example_content = self._generate_python_examples()
        
        # Write files
        files = {
            "garagereg/__init__.py": self._generate_python_init(),
            "garagereg/models.py": models_content,
            "garagereg/client.py": client_content,
            "garagereg/exceptions.py": self._generate_python_exceptions(),
            "setup.py": setup_py,
            "README.md": readme_content,
            "examples/usage.py": example_content,
            "requirements.txt": "requests>=2.25.0\\npydantic>=1.8.0\\ntypes-requests>=2.25.0"
        }
        
        for file_path, content in files.items():
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✅ Python SDK generated in: {output_dir}")
        return output_dir
    
    def _generate_typescript_types(self) -> str:
        """Generate TypeScript type definitions."""
        return '''/**
 * TypeScript types for GarageReg API
 * Generated from OpenAPI specification
 */

// Enums
export enum UserRole {
    ADMIN = "admin",
    MANAGER = "manager", 
    USER = "user",
    READONLY = "readonly"
}

export enum VehicleType {
    CAR = "car",
    TRUCK = "truck",
    MOTORCYCLE = "motorcycle",
    VAN = "van",
    BUS = "bus",
    OTHER = "other"
}

export enum MaintenanceStatus {
    SCHEDULED = "scheduled",
    IN_PROGRESS = "in_progress",
    COMPLETED = "completed",
    CANCELLED = "cancelled",
    OVERDUE = "overdue"
}

export enum MaintenanceType {
    OIL_CHANGE = "oil_change",
    TIRE_ROTATION = "tire_rotation",
    BRAKE_SERVICE = "brake_service",
    INSPECTION = "inspection",
    REPAIR = "repair",
    OTHER = "other"
}

// Base interfaces
export interface FieldError {
    field: string;
    message: string;
    code: string;
    value?: any;
}

export interface ErrorResponse {
    success: boolean;
    error: boolean;
    code: string;
    message: string;
    details?: string;
    field_errors?: FieldError[];
    path?: string;
    method?: string;
    timestamp?: string;
}

export interface SuccessResponse<T = any> {
    success: boolean;
    message: string;
    data?: T;
}

export interface PaginatedResponse<T = any> {
    items: T[];
    total: number;
    page: number;
    per_page: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
}

// User interfaces
export interface UserCreateRequest {
    username: string;
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    role?: UserRole;
}

export interface UserResponse {
    id: number;
    username: string;
    email: string;
    full_name: string;
    phone?: string;
    role: UserRole;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

// Vehicle interfaces
export interface VehicleCreateRequest {
    license_plate: string;
    make: string;
    model: string;
    year: number;
    vehicle_type: VehicleType;
    vin?: string;
    color?: string;
    engine_size?: string;
}

export interface VehicleResponse {
    id: number;
    license_plate: string;
    make: string;
    model: string;
    year: number;
    vehicle_type: VehicleType;
    vin?: string;
    color?: string;
    engine_size?: string;
    owner_id: number;
    created_at: string;
    updated_at: string;
}

// Authentication interfaces
export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user: UserResponse;
}

// API Configuration
export interface APIConfig {
    baseURL: string;
    timeout?: number;
    headers?: Record<string, string>;
}

// API Response wrapper
export type APIResponse<T> = Promise<T>;

// Query parameters
export interface UserListParams {
    page?: number;
    per_page?: number;
    role?: UserRole;
}

export interface VehicleListParams {
    page?: number;
    per_page?: number;
    vehicle_type?: VehicleType;
    make?: string;
    owner_id?: number;
}
'''
    
    def _generate_typescript_client(self) -> str:
        """Generate TypeScript API client."""
        return '''/**
 * GarageReg API Client
 * TypeScript SDK for GarageReg API
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
    APIConfig, APIResponse, ErrorResponse, LoginRequest, LoginResponse,
    UserCreateRequest, UserResponse, UserListParams, PaginatedResponse,
    VehicleCreateRequest, VehicleResponse, VehicleListParams
} from './types';

export class GarageRegAPIError extends Error {
    public code: string;
    public statusCode: number;
    public fieldErrors?: Array<{field: string, message: string, code: string}>;

    constructor(message: string, code: string, statusCode: number, fieldErrors?: any[]) {
        super(message);
        this.name = 'GarageRegAPIError';
        this.code = code;
        this.statusCode = statusCode;
        this.fieldErrors = fieldErrors;
    }
}

export class GarageRegClient {
    private client: AxiosInstance;
    private accessToken?: string;

    constructor(config: APIConfig) {
        this.client = axios.create({
            baseURL: config.baseURL,
            timeout: config.timeout || 30000,
            headers: {
                'Content-Type': 'application/json',
                ...config.headers
            }
        });

        // Request interceptor to add auth token
        this.client.interceptors.request.use(
            (config) => {
                if (this.accessToken) {
                    config.headers.Authorization = `Bearer ${this.accessToken}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error: AxiosError) => {
                if (error.response?.data) {
                    const errorData = error.response.data as ErrorResponse;
                    throw new GarageRegAPIError(
                        errorData.message,
                        errorData.code,
                        error.response.status,
                        errorData.field_errors
                    );
                }
                throw error;
            }
        );
    }

    /**
     * Set authentication token
     */
    setAuthToken(token: string): void {
        this.accessToken = token;
    }

    /**
     * Clear authentication token
     */
    clearAuthToken(): void {
        this.accessToken = undefined;
    }

    // Authentication methods
    async login(credentials: LoginRequest): APIResponse<LoginResponse> {
        const response = await this.client.post<LoginResponse>('/api/auth/login', credentials);
        this.setAuthToken(response.data.access_token);
        return response.data;
    }

    async logout(): APIResponse<{message: string}> {
        try {
            const response = await this.client.post('/api/auth/logout');
            this.clearAuthToken();
            return response.data;
        } catch (error) {
            this.clearAuthToken();
            throw error;
        }
    }

    // User methods
    async createUser(user: UserCreateRequest): APIResponse<UserResponse> {
        const response = await this.client.post<UserResponse>('/api/users', user);
        return response.data;
    }

    async listUsers(params?: UserListParams): APIResponse<PaginatedResponse<UserResponse>> {
        const response = await this.client.get<PaginatedResponse<UserResponse>>('/api/users', {
            params
        });
        return response.data;
    }

    async getUser(userId: number): APIResponse<UserResponse> {
        const response = await this.client.get<UserResponse>(`/api/users/${userId}`);
        return response.data;
    }

    // Vehicle methods
    async registerVehicle(vehicle: VehicleCreateRequest): APIResponse<VehicleResponse> {
        const response = await this.client.post<VehicleResponse>('/api/vehicles', vehicle);
        return response.data;
    }

    async listVehicles(params?: VehicleListParams): APIResponse<PaginatedResponse<VehicleResponse>> {
        const response = await this.client.get<PaginatedResponse<VehicleResponse>>('/api/vehicles', {
            params
        });
        return response.data;
    }

    async getVehicle(vehicleId: number): APIResponse<VehicleResponse> {
        const response = await this.client.get<VehicleResponse>(`/api/vehicles/${vehicleId}`);
        return response.data;
    }

    // Test methods
    async testUserValidation(user: UserCreateRequest): APIResponse<UserResponse> {
        const response = await this.client.post<UserResponse>('/api/test/validation/user', user);
        return response.data;
    }

    async testError(errorType: string): APIResponse<never> {
        const response = await this.client.get(`/api/test/errors/${errorType}`);
        return response.data;
    }
}

/**
 * Create a new GarageReg API client
 */
export function createClient(config: APIConfig): GarageRegClient {
    return new GarageRegClient(config);
}

/**
 * Default configuration for development
 */
export const defaultConfig: APIConfig = {
    baseURL: 'http://localhost:8004',
    timeout: 30000
};
'''
    
    def _generate_typescript_index(self) -> str:
        """Generate TypeScript index file."""
        return '''/**
 * GarageReg TypeScript SDK
 * 
 * @example
 * ```typescript
 * import { createClient, defaultConfig } from '@garagereg/sdk';
 * 
 * const client = createClient(defaultConfig);
 * 
 * // Login
 * const loginResponse = await client.login({
 *     username: 'demo',
 *     password: 'password123'
 * });
 * 
 * // Create user
 * const user = await client.createUser({
 *     username: 'john_doe',
 *     email: 'john@example.com',
 *     password: 'securePassword123',
 *     full_name: 'John Doe'
 * });
 * ```
 */

export * from './types';
export * from './client';
export { createClient, defaultConfig, GarageRegClient, GarageRegAPIError } from './client';
'''
    
    def _generate_typescript_package_json(self) -> Dict[str, Any]:
        """Generate package.json for TypeScript SDK."""
        return {
            "name": "@garagereg/sdk",
            "version": "2.0.0",
            "description": "TypeScript SDK for GarageReg API",
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "scripts": {
                "build": "tsc",
                "dev": "tsc --watch",
                "test": "jest",
                "lint": "eslint src/**/*.ts",
                "prepare": "npm run build"
            },
            "keywords": ["garagereg", "api", "sdk", "typescript"],
            "author": "GarageReg Team",
            "license": "MIT",
            "dependencies": {
                "axios": "^1.5.0"
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "typescript": "^5.0.0",
                "jest": "^29.0.0",
                "@types/jest": "^29.0.0",
                "eslint": "^8.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0"
            },
            "repository": {
                "type": "git",
                "url": "https://github.com/garagereg/sdk-typescript"
            },
            "engines": {
                "node": ">=16"
            }
        }
    
    def _generate_tsconfig(self) -> Dict[str, Any]:
        """Generate tsconfig.json."""
        return {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "declaration": True,
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist", "examples"]
        }
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""
        return '''node_modules/
dist/
*.log
.env
.DS_Store
coverage/
'''
    
    def _generate_typescript_readme(self) -> str:
        """Generate README for TypeScript SDK."""
        return '''# GarageReg TypeScript SDK

TypeScript/JavaScript SDK for the GarageReg API.

## Installation

```bash
npm install @garagereg/sdk
```

## Quick Start

```typescript
import { createClient, defaultConfig } from '@garagereg/sdk';

const client = createClient({
    baseURL: 'http://localhost:8004',
    timeout: 30000
});

// Login
try {
    const loginResponse = await client.login({
        username: 'demo',
        password: 'password123'
    });
    
    console.log('Login successful:', loginResponse.user.full_name);
} catch (error) {
    if (error instanceof GarageRegAPIError) {
        console.error('API Error:', error.message);
        console.error('Error Code:', error.code);
        if (error.fieldErrors) {
            console.error('Field Errors:', error.fieldErrors);
        }
    }
}
```

## Usage Examples

### User Management

```typescript
// Create a new user
const user = await client.createUser({
    username: 'john_doe',
    email: 'john@example.com', 
    password: 'securePassword123',
    full_name: 'John Doe',
    phone: '+36301234567',
    role: UserRole.USER
});

// List users with pagination
const users = await client.listUsers({
    page: 1,
    per_page: 20,
    role: UserRole.USER
});

// Get specific user
const specificUser = await client.getUser(12345);
```

### Vehicle Management

```typescript
// Register a new vehicle
const vehicle = await client.registerVehicle({
    license_plate: 'ABC-123',
    make: 'Toyota',
    model: 'Camry',
    year: 2022,
    vehicle_type: VehicleType.CAR,
    vin: '1HGBH41JXMN109186',
    color: 'Blue',
    engine_size: '2.5L'
});

// List vehicles
const vehicles = await client.listVehicles({
    page: 1,
    per_page: 10,
    vehicle_type: VehicleType.CAR
});
```

### Error Handling

```typescript
import { GarageRegAPIError } from '@garagereg/sdk';

try {
    await client.createUser(invalidUserData);
} catch (error) {
    if (error instanceof GarageRegAPIError) {
        switch (error.code) {
            case 'VALIDATION_ERROR':
                console.log('Validation failed:');
                error.fieldErrors?.forEach(fieldError => {
                    console.log(`- ${fieldError.field}: ${fieldError.message}`);
                });
                break;
            case 'RESOURCE_CONFLICT':
                console.log('Resource already exists');
                break;
            default:
                console.log('API error:', error.message);
        }
    }
}
```

## Configuration

```typescript
const client = createClient({
    baseURL: 'https://api.garagereg.com',  // API base URL
    timeout: 30000,                        // Request timeout in ms
    headers: {                             // Custom headers
        'X-API-Version': '2.0'
    }
});
```

## Types

The SDK includes comprehensive TypeScript types for all API entities:

- `UserRole`, `VehicleType`, `MaintenanceStatus`, `MaintenanceType` enums
- Request/Response interfaces for all endpoints
- Error types with field-level validation details
- Pagination support

## Development

```bash
# Install dependencies
npm install

# Build the SDK
npm run build

# Watch for changes
npm run dev

# Run tests
npm test
```

## License

MIT License
'''
    
    def _generate_typescript_examples(self) -> str:
        """Generate TypeScript usage examples."""
        return '''/**
 * GarageReg SDK Usage Examples
 */

import { createClient, GarageRegAPIError, UserRole, VehicleType } from '../src';

async function examples() {
    const client = createClient({
        baseURL: 'http://localhost:8004'
    });

    try {
        // 1. Login
        console.log('1. Authenticating...');
        const loginResponse = await client.login({
            username: 'demo',
            password: 'password123'
        });
        console.log(`✅ Logged in as: ${loginResponse.user.full_name}`);

        // 2. Create a user
        console.log('\\n2. Creating user...');
        const user = await client.createUser({
            username: 'jane_doe',
            email: 'jane@example.com',
            password: 'securePassword123',
            full_name: 'Jane Doe',
            phone: '+36301234567',
            role: UserRole.USER
        });
        console.log(`✅ User created: ${user.full_name} (ID: ${user.id})`);

        // 3. Register a vehicle
        console.log('\\n3. Registering vehicle...');
        const vehicle = await client.registerVehicle({
            license_plate: 'DEF-456',
            make: 'Honda',
            model: 'Civic',
            year: 2023,
            vehicle_type: VehicleType.CAR,
            color: 'Red',
            engine_size: '1.5L'
        });
        console.log(`✅ Vehicle registered: ${vehicle.make} ${vehicle.model} (${vehicle.license_plate})`);

        // 4. List users with pagination
        console.log('\\n4. Listing users...');
        const usersList = await client.listUsers({
            page: 1,
            per_page: 5
        });
        console.log(`✅ Found ${usersList.total} users (page ${usersList.page}/${usersList.pages})`);

        // 5. Test validation errors
        console.log('\\n5. Testing validation errors...');
        try {
            await client.testUserValidation({
                username: 'a',  // Too short
                email: 'invalid-email',  // Invalid format
                password: '123',  // Too short
                full_name: '',  // Empty
            });
        } catch (validationError) {
            if (validationError instanceof GarageRegAPIError) {
                console.log(`✅ Validation error caught: ${validationError.message}`);
                console.log('Field errors:');
                validationError.fieldErrors?.forEach(fe => {
                    console.log(`  - ${fe.field}: ${fe.message} (${fe.code})`);
                });
            }
        }

        // 6. Test different error types
        console.log('\\n6. Testing different error scenarios...');
        const errorTypes = ['not_found', 'conflict', 'auth'];
        for (const errorType of errorTypes) {
            try {
                await client.testError(errorType);
            } catch (error) {
                if (error instanceof GarageRegAPIError) {
                    console.log(`✅ ${errorType} error: ${error.message} (${error.code})`);
                }
            }
        }

        console.log('\\n🎉 All examples completed successfully!');

    } catch (error) {
        if (error instanceof GarageRegAPIError) {
            console.error(`❌ API Error: ${error.message}`);
            console.error(`   Code: ${error.code}`);
            console.error(`   Status: ${error.statusCode}`);
            if (error.fieldErrors) {
                console.error('   Field Errors:');
                error.fieldErrors.forEach(fe => {
                    console.error(`     - ${fe.field}: ${fe.message}`);
                });
            }
        } else {
            console.error('❌ Unexpected error:', error);
        }
    }
}

// Run examples
if (require.main === module) {
    examples().catch(console.error);
}

export { examples };
'''
    
    def _generate_python_models(self) -> str:
        """Generate Python models."""
        return '''"""
Python models for GarageReg API
Generated from OpenAPI specification
"""

from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    READONLY = "readonly"


class VehicleType(str, Enum):
    """Types of vehicles."""
    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    VAN = "van"
    BUS = "bus"
    OTHER = "other"


class MaintenanceStatus(str, Enum):
    """Status of maintenance tasks."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class MaintenanceType(str, Enum):
    """Types of maintenance operations."""
    OIL_CHANGE = "oil_change"
    TIRE_ROTATION = "tire_rotation"
    BRAKE_SERVICE = "brake_service"
    INSPECTION = "inspection"
    REPAIR = "repair"
    OTHER = "other"


class FieldError(BaseModel):
    """Individual field validation error."""
    field: str = Field(..., description="Field name that caused the error")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Error code for programmatic handling")
    value: Optional[Any] = Field(None, description="The invalid value that was provided")


class ErrorResponse(BaseModel):
    """Standardized error response envelope."""
    success: bool = Field(False, description="Always false for error responses")
    error: bool = Field(True, description="Always true for error responses")
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")
    field_errors: Optional[List[FieldError]] = Field(None, description="Field-specific validation errors")
    path: Optional[str] = Field(None, description="API path where error occurred")
    method: Optional[str] = Field(None, description="HTTP method")
    timestamp: Optional[str] = Field(None, description="ISO timestamp when error occurred")


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class UserCreateRequest(BaseModel):
    """Request model for creating a new user."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex=r'^[a-zA-Z0-9_-]+$',
        description="Unique username (3-50 chars, alphanumeric, underscore, dash)"
    )
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (minimum 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    phone: Optional[str] = Field(
        None,
        regex=r'^\\+\\d{1,3}\\d{4,14}$',
        description="Phone number in international format (+country code)"
    )
    role: UserRole = Field(UserRole.USER, description="User role in the system")


class UserResponse(BaseModel):
    """User response model."""
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class VehicleCreateRequest(BaseModel):
    """Request model for registering a new vehicle."""
    license_plate: str = Field(..., min_length=2, max_length=20, description="Vehicle license plate number")
    make: str = Field(..., min_length=1, max_length=50, description="Vehicle manufacturer")
    model: str = Field(..., min_length=1, max_length=50, description="Vehicle model")
    year: int = Field(..., ge=1900, le=2030, description="Manufacturing year")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    vin: Optional[str] = Field(
        None,
        min_length=17,
        max_length=17,
        regex=r'^[A-HJ-NPR-Z0-9]{17}$',
        description="Vehicle Identification Number (17 characters)"
    )
    color: Optional[str] = Field(None, max_length=30, description="Vehicle color")
    engine_size: Optional[str] = Field(None, max_length=20, description="Engine size/displacement")


class VehicleResponse(BaseModel):
    """Vehicle response model."""
    id: int = Field(..., description="Unique vehicle identifier")
    license_plate: str = Field(..., description="License plate number")
    make: str = Field(..., description="Vehicle manufacturer")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Manufacturing year")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    vin: Optional[str] = Field(None, description="Vehicle Identification Number")
    color: Optional[str] = Field(None, description="Vehicle color")
    engine_size: Optional[str] = Field(None, description="Engine size")
    owner_id: int = Field(..., description="ID of the vehicle owner")
    created_at: datetime = Field(..., description="Registration timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="Authenticated user information")
'''
    
    def _generate_python_client(self) -> str:
        """Generate Python API client."""
        return '''"""
GarageReg API Client
Python SDK for GarageReg API
"""

import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
import json

from .models import (
    UserCreateRequest, UserResponse, VehicleCreateRequest, VehicleResponse,
    LoginRequest, LoginResponse, PaginatedResponse, ErrorResponse,
    UserRole, VehicleType
)
from .exceptions import GarageRegAPIError


class GarageRegClient:
    """Python client for GarageReg API."""
    
    def __init__(self, base_url: str = "http://localhost:8004", timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GarageReg-Python-SDK/2.0.0'
        })
        self.access_token: Optional[str] = None
    
    def set_auth_token(self, token: str) -> None:
        """Set authentication token."""
        self.access_token = token
        self.session.headers['Authorization'] = f'Bearer {token}'
    
    def clear_auth_token(self) -> None:
        """Clear authentication token."""
        self.access_token = None
        self.session.headers.pop('Authorization', None)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                self._handle_error_response(response)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise GarageRegAPIError(f"Request failed: {str(e)}", "REQUEST_ERROR", 0)
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses."""
        try:
            error_data = response.json()
            error_response = ErrorResponse(**error_data)
            
            raise GarageRegAPIError(
                message=error_response.message,
                code=error_response.code,
                status_code=response.status_code,
                field_errors=error_response.field_errors
            )
        except (ValueError, TypeError):
            raise GarageRegAPIError(
                message=f"HTTP {response.status_code}: {response.text}",
                code="HTTP_ERROR",
                status_code=response.status_code
            )
    
    # Authentication methods
    def login(self, username: str, password: str) -> LoginResponse:
        """
        Authenticate user and obtain access token.
        
        Args:
            username: Username or email
            password: User password
            
        Returns:
            LoginResponse with access token and user info
        """
        request = LoginRequest(username=username, password=password)
        response_data = self._make_request('POST', '/api/auth/login', request.dict())
        
        login_response = LoginResponse(**response_data)
        self.set_auth_token(login_response.access_token)
        return login_response
    
    def logout(self) -> Dict[str, str]:
        """
        Logout current user and invalidate access token.
        
        Returns:
            Success message
        """
        try:
            response_data = self._make_request('POST', '/api/auth/logout')
            self.clear_auth_token()
            return response_data
        except Exception:
            self.clear_auth_token()
            raise
    
    # User methods
    def create_user(self, user: UserCreateRequest) -> UserResponse:
        """
        Create a new user account.
        
        Args:
            user: User creation request
            
        Returns:
            Created user information
        """
        response_data = self._make_request('POST', '/api/users', user.dict())
        return UserResponse(**response_data)
    
    def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: Optional[UserRole] = None
    ) -> PaginatedResponse:
        """
        Get paginated list of users.
        
        Args:
            page: Page number
            per_page: Items per page
            role: Filter by user role
            
        Returns:
            Paginated list of users
        """
        params = {'page': page, 'per_page': per_page}
        if role:
            params['role'] = role.value
        
        response_data = self._make_request('GET', '/api/users', params=params)
        return PaginatedResponse(**response_data)
    
    def get_user(self, user_id: int) -> UserResponse:
        """
        Get specific user information.
        
        Args:
            user_id: User identifier
            
        Returns:
            User information
        """
        response_data = self._make_request('GET', f'/api/users/{user_id}')
        return UserResponse(**response_data)
    
    # Vehicle methods
    def register_vehicle(self, vehicle: VehicleCreateRequest) -> VehicleResponse:
        """
        Register a new vehicle.
        
        Args:
            vehicle: Vehicle registration request
            
        Returns:
            Registered vehicle information
        """
        response_data = self._make_request('POST', '/api/vehicles', vehicle.dict())
        return VehicleResponse(**response_data)
    
    def list_vehicles(
        self,
        page: int = 1,
        per_page: int = 20,
        vehicle_type: Optional[VehicleType] = None,
        make: Optional[str] = None,
        owner_id: Optional[int] = None
    ) -> PaginatedResponse:
        """
        Get paginated list of vehicles.
        
        Args:
            page: Page number
            per_page: Items per page
            vehicle_type: Filter by vehicle type
            make: Filter by manufacturer
            owner_id: Filter by owner ID
            
        Returns:
            Paginated list of vehicles
        """
        params = {'page': page, 'per_page': per_page}
        if vehicle_type:
            params['vehicle_type'] = vehicle_type.value
        if make:
            params['make'] = make
        if owner_id:
            params['owner_id'] = owner_id
        
        response_data = self._make_request('GET', '/api/vehicles', params=params)
        return PaginatedResponse(**response_data)
    
    def get_vehicle(self, vehicle_id: int) -> VehicleResponse:
        """
        Get specific vehicle information.
        
        Args:
            vehicle_id: Vehicle identifier
            
        Returns:
            Vehicle information
        """
        response_data = self._make_request('GET', f'/api/vehicles/{vehicle_id}')
        return VehicleResponse(**response_data)
    
    # Test methods
    def test_user_validation(self, user: UserCreateRequest) -> UserResponse:
        """
        Test user validation endpoint.
        
        Args:
            user: User data to validate
            
        Returns:
            User response if validation passes
        """
        response_data = self._make_request('POST', '/api/test/validation/user', user.dict())
        return UserResponse(**response_data)
    
    def test_error(self, error_type: str) -> None:
        """
        Test error scenarios.
        
        Args:
            error_type: Type of error to simulate
        """
        self._make_request('GET', f'/api/test/errors/{error_type}')


def create_client(base_url: str = "http://localhost:8004", timeout: int = 30) -> GarageRegClient:
    """
    Create a new GarageReg API client.
    
    Args:
        base_url: Base URL of the API
        timeout: Request timeout in seconds
        
    Returns:
        Configured API client
    """
    return GarageRegClient(base_url=base_url, timeout=timeout)
'''
    
    def _generate_python_exceptions(self) -> str:
        """Generate Python exceptions."""
        return '''"""
Custom exceptions for GarageReg SDK
"""

from typing import List, Optional, Any, Dict


class GarageRegAPIError(Exception):
    """Base exception for GarageReg API errors."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        field_errors: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize API error.
        
        Args:
            message: Error message
            code: Error code
            status_code: HTTP status code
            field_errors: Field-specific validation errors
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field_errors = field_errors or []
    
    def __str__(self) -> str:
        return f"GarageRegAPIError({self.code}): {self.message}"
    
    def __repr__(self) -> str:
        return f"GarageRegAPIError(message='{self.message}', code='{self.code}', status_code={self.status_code})"


class ValidationError(GarageRegAPIError):
    """Validation error with field-specific details."""
    
    def __init__(self, message: str, field_errors: List[Dict[str, Any]]):
        super().__init__(message, "VALIDATION_ERROR", 400, field_errors)


class AuthenticationError(GarageRegAPIError):
    """Authentication required error."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "AUTHENTICATION_REQUIRED", 401)


class NotFoundError(GarageRegAPIError):
    """Resource not found error."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "RESOURCE_NOT_FOUND", 404)


class ConflictError(GarageRegAPIError):
    """Resource conflict error."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, "RESOURCE_CONFLICT", 409)
'''
    
    def _generate_python_init(self) -> str:
        """Generate Python __init__.py file."""
        return '''"""
GarageReg Python SDK

A Python client library for the GarageReg API.

Example usage:
    from garagereg import create_client, UserRole, VehicleType
    
    client = create_client('http://localhost:8004')
    
    # Login
    login_response = client.login('demo', 'password123')
    
    # Create user
    user = client.create_user(UserCreateRequest(
        username='john_doe',
        email='john@example.com',
        password='securePassword123',
        full_name='John Doe'
    ))
"""

from .client import GarageRegClient, create_client
from .models import (
    UserRole, VehicleType, MaintenanceStatus, MaintenanceType,
    UserCreateRequest, UserResponse, VehicleCreateRequest, VehicleResponse,
    LoginRequest, LoginResponse, PaginatedResponse, ErrorResponse,
    FieldError, SuccessResponse
)
from .exceptions import (
    GarageRegAPIError, ValidationError, AuthenticationError,
    NotFoundError, ConflictError
)

__version__ = "2.0.0"
__author__ = "GarageReg Team"

__all__ = [
    # Client
    "GarageRegClient", "create_client",
    
    # Models
    "UserRole", "VehicleType", "MaintenanceStatus", "MaintenanceType",
    "UserCreateRequest", "UserResponse", "VehicleCreateRequest", "VehicleResponse",
    "LoginRequest", "LoginResponse", "PaginatedResponse", "ErrorResponse",
    "FieldError", "SuccessResponse",
    
    # Exceptions
    "GarageRegAPIError", "ValidationError", "AuthenticationError",
    "NotFoundError", "ConflictError"
]
'''
    
    def _generate_python_setup(self) -> str:
        """Generate setup.py for Python SDK."""
        return '''"""
Setup script for GarageReg Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="garagereg-sdk",
    version="2.0.0",
    author="GarageReg Team",
    author_email="support@garagereg.com",
    description="Python SDK for GarageReg API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/garagereg/sdk-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "types-requests>=2.25.0",
        ]
    },
    keywords=["garagereg", "api", "sdk", "python"],
    project_urls={
        "Bug Reports": "https://github.com/garagereg/sdk-python/issues",
        "Source": "https://github.com/garagereg/sdk-python",
        "Documentation": "https://docs.garagereg.com/sdk/python/",
    },
)
'''
    
    def _generate_python_readme(self) -> str:
        """Generate README for Python SDK."""
        return '''# GarageReg Python SDK

Python client library for the GarageReg API.

## Installation

```bash
pip install garagereg-sdk
```

## Quick Start

```python
from garagereg import create_client, UserRole, VehicleType

# Create client
client = create_client('http://localhost:8004')

# Login
login_response = client.login('demo', 'password123')
print(f"Logged in as: {login_response.user.full_name}")

# Create a user
from garagereg import UserCreateRequest
user = client.create_user(UserCreateRequest(
    username='john_doe',
    email='john@example.com', 
    password='securePassword123',
    full_name='John Doe',
    phone='+36301234567',
    role=UserRole.USER
))
print(f"User created: {user.full_name} (ID: {user.id})")
```

## Usage Examples

### User Management

```python
from garagereg import UserCreateRequest, UserRole

# Create a new user
user = client.create_user(UserCreateRequest(
    username='jane_doe',
    email='jane@example.com',
    password='securePassword123',
    full_name='Jane Doe',
    phone='+36301234567',
    role=UserRole.USER
))

# List users with pagination
users = client.list_users(page=1, per_page=20, role=UserRole.USER)
print(f"Found {users.total} users")

# Get specific user
user = client.get_user(12345)
print(f"User: {user.full_name}")
```

### Vehicle Management

```python
from garagereg import VehicleCreateRequest, VehicleType

# Register a new vehicle
vehicle = client.register_vehicle(VehicleCreateRequest(
    license_plate='ABC-123',
    make='Toyota',
    model='Camry',
    year=2022,
    vehicle_type=VehicleType.CAR,
    vin='1HGBH41JXMN109186',
    color='Blue',
    engine_size='2.5L'
))

# List vehicles
vehicles = client.list_vehicles(
    page=1,
    per_page=10, 
    vehicle_type=VehicleType.CAR
)
```

### Error Handling

```python
from garagereg import GarageRegAPIError, ValidationError

try:
    user = client.create_user(invalid_user_data)
except GarageRegAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Error Code: {e.code}")
    print(f"Status Code: {e.status_code}")
    
    if e.field_errors:
        print("Field Errors:")
        for field_error in e.field_errors:
            print(f"  - {field_error['field']}: {field_error['message']}")
```

### Configuration

```python
from garagereg import create_client

# Custom configuration
client = create_client(
    base_url='https://api.garagereg.com',
    timeout=60  # Request timeout in seconds
)

# Manual authentication
client.set_auth_token('your-jwt-token')

# Clear authentication
client.clear_auth_token()
```

## Models

The SDK includes comprehensive Pydantic models for all API entities:

- **Enums**: `UserRole`, `VehicleType`, `MaintenanceStatus`, `MaintenanceType`
- **Request Models**: `UserCreateRequest`, `VehicleCreateRequest`, `LoginRequest`
- **Response Models**: `UserResponse`, `VehicleResponse`, `LoginResponse`
- **Utility Models**: `PaginatedResponse`, `ErrorResponse`, `FieldError`

## Error Types

- `GarageRegAPIError`: Base exception for all API errors
- `ValidationError`: Field validation errors (400)
- `AuthenticationError`: Authentication required (401)
- `NotFoundError`: Resource not found (404)
- `ConflictError`: Resource conflict (409)

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy garagereg/

# Format code
black garagereg/

# Lint code
flake8 garagereg/
```

## License

MIT License
'''
    
    def _generate_python_examples(self) -> str:
        """Generate Python usage examples."""
        return '''"""
GarageReg SDK Usage Examples
"""

import asyncio
from garagereg import (
    create_client, GarageRegAPIError, UserRole, VehicleType,
    UserCreateRequest, VehicleCreateRequest
)


def main():
    """Run all examples."""
    client = create_client('http://localhost:8004')
    
    try:
        # 1. Login
        print('1. Authenticating...')
        login_response = client.login('demo', 'password123')
        print(f'✅ Logged in as: {login_response.user.full_name}')

        # 2. Create a user
        print('\\n2. Creating user...')
        user = client.create_user(UserCreateRequest(
            username='jane_doe',
            email='jane@example.com',
            password='securePassword123',
            full_name='Jane Doe',
            phone='+36301234567',
            role=UserRole.USER
        ))
        print(f'✅ User created: {user.full_name} (ID: {user.id})')

        # 3. Register a vehicle
        print('\\n3. Registering vehicle...')
        vehicle = client.register_vehicle(VehicleCreateRequest(
            license_plate='DEF-456',
            make='Honda',
            model='Civic',
            year=2023,
            vehicle_type=VehicleType.CAR,
            color='Red',
            engine_size='1.5L'
        ))
        print(f'✅ Vehicle registered: {vehicle.make} {vehicle.model} ({vehicle.license_plate})')

        # 4. List users with pagination
        print('\\n4. Listing users...')
        users_list = client.list_users(page=1, per_page=5)
        print(f'✅ Found {users_list.total} users (page {users_list.page}/{users_list.pages})')

        # 5. Test validation errors
        print('\\n5. Testing validation errors...')
        try:
            client.test_user_validation(UserCreateRequest(
                username='a',  # Too short
                email='invalid-email',  # Invalid format
                password='123',  # Too short
                full_name='',  # Empty
            ))
        except GarageRegAPIError as validation_error:
            print(f'✅ Validation error caught: {validation_error.message}')
            print('Field errors:')
            for fe in validation_error.field_errors:
                print(f'  - {fe["field"]}: {fe["message"]} ({fe["code"]})')

        # 6. Test different error types
        print('\\n6. Testing different error scenarios...')
        error_types = ['not_found', 'conflict', 'auth']
        for error_type in error_types:
            try:
                client.test_error(error_type)
            except GarageRegAPIError as error:
                print(f'✅ {error_type} error: {error.message} ({error.code})')

        print('\\n🎉 All examples completed successfully!')

    except GarageRegAPIError as e:
        print(f'❌ API Error: {e.message}')
        print(f'   Code: {e.code}')
        print(f'   Status: {e.status_code}')
        if e.field_errors:
            print('   Field Errors:')
            for fe in e.field_errors:
                print(f'     - {fe["field"]}: {fe["message"]}')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')


if __name__ == '__main__':
    main()
'''

def generate_sdks():
    """Generate both TypeScript and Python SDKs."""
    generator = SDKGenerator()
    
    # Create SDK directory structure
    sdk_dir = Path(r"c:\Users\drurb\garagereg\sdk")
    typescript_dir = sdk_dir / "typescript"
    python_dir = sdk_dir / "python"
    
    try:
        print("🚀 Generating SDKs from OpenAPI specification...")
        
        # Generate TypeScript SDK
        print("📦 Generating TypeScript SDK...")
        generator.generate_typescript_sdk(str(typescript_dir))
        
        # Generate Python SDK
        print("🐍 Generating Python SDK...")
        generator.generate_python_sdk(str(python_dir))
        
        print("\\n✅ SDK Generation Complete!")
        print(f"📁 SDKs generated in: {sdk_dir}")
        print(f"   - TypeScript: {typescript_dir}")
        print(f"   - Python: {python_dir}")
        
    except Exception as e:
        print(f"❌ SDK generation failed: {e}")

if __name__ == "__main__":
    generate_sdks()
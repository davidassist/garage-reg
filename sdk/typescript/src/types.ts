/**
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
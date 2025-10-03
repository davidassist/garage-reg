/**
 * GarageReg API Client
 * TypeScript SDK for GarageReg API
 */

// Simple HTTP client without external dependencies
class SimpleHTTPClient {
    private baseURL: string;
    private defaultHeaders: Record<string, string>;
    private accessToken?: string;

    constructor(baseURL: string, headers: Record<string, string> = {}) {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            ...headers
        };
    }

    setAuthToken(token: string): void {
        this.accessToken = token;
    }

    clearAuthToken(): void {
        this.accessToken = undefined;
    }

    private getHeaders(): Record<string, string> {
        const headers = { ...this.defaultHeaders };
        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }
        return headers;
    }

    async request<T>(method: string, path: string, data?: any): Promise<T> {
        const url = `${this.baseURL}${path}`;
        const headers = this.getHeaders();

        const options: RequestInit = {
            method,
            headers,
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const responseData = await response.json();

            if (!response.ok) {
                throw new GarageRegAPIError(
                    responseData.message || 'API Error',
                    responseData.code || 'API_ERROR',
                    response.status,
                    responseData.field_errors
                );
            }

            return responseData;
        } catch (error) {
            if (error instanceof GarageRegAPIError) {
                throw error;
            }
            throw new GarageRegAPIError(
                'Network Error',
                'NETWORK_ERROR',
                500
            );
        }
    }

    async get<T>(path: string, params?: Record<string, any>): Promise<T> {
        let url = path;
        if (params) {
            const searchParams = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    searchParams.append(key, String(value));
                }
            });
            const queryString = searchParams.toString();
            if (queryString) {
                url += `?${queryString}`;
            }
        }
        return this.request<T>('GET', url);
    }

    async post<T>(path: string, data?: any): Promise<T> {
        return this.request<T>('POST', path, data);
    }
}

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
    private client: SimpleHTTPClient;

    constructor(config: APIConfig) {
        this.client = new SimpleHTTPClient(
            config.baseURL,
            config.headers
        );
    }

    /**
     * Set authentication token
     */
    setAuthToken(token: string): void {
        this.client.setAuthToken(token);
    }

    /**
     * Clear authentication token
     */
    clearAuthToken(): void {
        this.client.clearAuthToken();
    }

    // Authentication methods
    async login(credentials: LoginRequest): Promise<LoginResponse> {
        const response = await this.client.post<LoginResponse>('/api/auth/login', credentials);
        this.setAuthToken(response.access_token);
        return response;
    }

    async logout(): Promise<{message: string}> {
        try {
            const response = await this.client.post<{message: string}>('/api/auth/logout');
            this.clearAuthToken();
            return response;
        } catch (error) {
            this.clearAuthToken();
            throw error;
        }
    }

    // User methods
    async createUser(user: UserCreateRequest): Promise<UserResponse> {
        return this.client.post<UserResponse>('/api/users', user);
    }

    async listUsers(params?: UserListParams): Promise<PaginatedResponse<UserResponse>> {
        return this.client.get<PaginatedResponse<UserResponse>>('/api/users', params);
    }

    async getUser(userId: number): Promise<UserResponse> {
        return this.client.get<UserResponse>(`/api/users/${userId}`);
    }

    // Vehicle methods
    async registerVehicle(vehicle: VehicleCreateRequest): Promise<VehicleResponse> {
        return this.client.post<VehicleResponse>('/api/vehicles', vehicle);
    }

    async listVehicles(params?: VehicleListParams): Promise<PaginatedResponse<VehicleResponse>> {
        return this.client.get<PaginatedResponse<VehicleResponse>>('/api/vehicles', params);
    }

    async getVehicle(vehicleId: number): Promise<VehicleResponse> {
        return this.client.get<VehicleResponse>(`/api/vehicles/${vehicleId}`);
    }

    // Test methods
    async testUserValidation(user: UserCreateRequest): Promise<UserResponse> {
        return this.client.post<UserResponse>('/api/test/validation/user', user);
    }

    async testError(errorType: string): Promise<ErrorResponse> {
        return this.client.get<ErrorResponse>(`/api/test/errors/${errorType}`);
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
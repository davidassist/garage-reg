# GarageReg TypeScript SDK

A TypeScript client library for the GarageReg API.

## Installation

```bash
npm install @garagereg/api-client
```

## Usage

```typescript
import { GarageRegClient, defaultConfig } from '@garagereg/api-client';

// Create client with default configuration
const client = new GarageRegClient(defaultConfig);

// Or with custom configuration
const client = new GarageRegClient({
    baseURL: 'https://api.garagereg.com',
    timeout: 30000,
    headers: {
        'Custom-Header': 'value'
    }
});

// Authentication
try {
    const loginResponse = await client.login({
        username: 'admin@example.com',
        password: 'password123'
    });
    console.log('Logged in:', loginResponse.user);
} catch (error) {
    console.error('Login failed:', error);
}

// Create a user
try {
    const user = await client.createUser({
        username: 'john_doe',
        email: 'john@example.com',
        password: 'password123',
        full_name: 'John Doe'
    });
    console.log('User created:', user);
} catch (error) {
    console.error('User creation failed:', error);
}

// List users with pagination
const users = await client.listUsers({
    skip: 0,
    limit: 10,
    search: 'john'
});
console.log('Users:', users.items);
console.log('Total:', users.total);

// Register a vehicle
const vehicle = await client.registerVehicle({
    license_plate: 'ABC-123',
    make: 'Toyota',
    model: 'Camry',
    year: 2022,
    color: 'Blue',
    vin: '1HGCM82633A123456',
    owner_id: 1
});
console.log('Vehicle registered:', vehicle);

// Error handling
try {
    await client.testError('validation');
} catch (error) {
    if (error instanceof GarageRegAPIError) {
        console.log('Error code:', error.code);
        console.log('Status:', error.statusCode);
        if (error.fieldErrors) {
            console.log('Field errors:', error.fieldErrors);
        }
    }
}
```

## API Reference

### Authentication

- `login(credentials: LoginRequest): Promise<LoginResponse>`
- `logout(): Promise<{message: string}>`

### Users

- `createUser(user: UserCreateRequest): Promise<UserResponse>`
- `listUsers(params?: UserListParams): Promise<PaginatedResponse<UserResponse>>`
- `getUser(userId: number): Promise<UserResponse>`

### Vehicles

- `registerVehicle(vehicle: VehicleCreateRequest): Promise<VehicleResponse>`
- `listVehicles(params?: VehicleListParams): Promise<PaginatedResponse<VehicleResponse>>`
- `getVehicle(vehicleId: number): Promise<VehicleResponse>`

### Testing

- `testUserValidation(user: UserCreateRequest): Promise<UserResponse>`
- `testError(errorType: string): Promise<ErrorResponse>`

## Error Handling

The SDK throws `GarageRegAPIError` for API errors, which includes:

- `message`: Error message
- `code`: Error code
- `statusCode`: HTTP status code
- `fieldErrors`: Array of field-specific validation errors (if any)

## License

MIT
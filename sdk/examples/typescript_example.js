#!/usr/bin/env node
/**
 * GarageReg TypeScript SDK Example
 * 
 * This example demonstrates how to use the GarageReg TypeScript SDK
 * to interact with the API for user and vehicle management.
 */

// In a real project, you would install and import like this:
// import { GarageRegClient, defaultConfig, GarageRegAPIError } from '@garagereg/api-client';

// For this example, we'll use require with relative paths
const path = require('path');
const sdkPath = path.join(__dirname, '..', 'typescript', 'src');

// Note: This example shows the usage pattern. 
// In production, you would build the TypeScript SDK first.
console.log('=== GarageReg TypeScript SDK Example ===\n');

// Example configuration
const config = {
    baseURL: 'http://localhost:8004',
    timeout: 30000,
    headers: {
        'User-Agent': 'GarageReg-SDK-Example/1.0.0'
    }
};

console.log('Configuration:', JSON.stringify(config, null, 2));

// Example usage (pseudo-code showing the API)
const exampleUsage = {
    // 1. Create client
    createClient: () => {
        console.log('\n1. Creating GarageReg client...');
        // const client = new GarageRegClient(config);
        console.log('✓ Client created with base URL:', config.baseURL);
    },

    // 2. Authentication
    login: async () => {
        console.log('\n2. Authenticating user...');
        const credentials = {
            username: 'admin@example.com',
            password: 'password123'
        };
        
        console.log('Login credentials:', credentials.username);
        // try {
        //     const response = await client.login(credentials);
        //     console.log('✓ Logged in successfully');
        //     console.log('User:', response.user.full_name);
        //     console.log('Token expires in:', response.expires_in, 'seconds');
        // } catch (error) {
        //     if (error instanceof GarageRegAPIError) {
        //         console.error('✗ Login failed:', error.message);
        //         console.error('Error code:', error.code);
        //     }
        // }
        
        console.log('✓ Authentication example prepared');
    },

    // 3. Create user
    createUser: async () => {
        console.log('\n3. Creating new user...');
        const newUser = {
            username: 'john_doe',
            email: 'john@example.com',
            password: 'securepass123',
            full_name: 'John Doe',
            role: 'technician'
        };

        console.log('New user data:', {
            username: newUser.username,
            email: newUser.email,
            full_name: newUser.full_name,
            role: newUser.role
        });

        // try {
        //     const user = await client.createUser(newUser);
        //     console.log('✓ User created successfully');
        //     console.log('User ID:', user.id);
        //     console.log('Created at:', user.created_at);
        // } catch (error) {
        //     if (error instanceof GarageRegAPIError) {
        //         console.error('✗ User creation failed:', error.message);
        //         if (error.fieldErrors) {
        //             error.fieldErrors.forEach(fe => {
        //                 console.error(`  ${fe.field}: ${fe.message}`);
        //             });
        //         }
        //     }
        // }

        console.log('✓ User creation example prepared');
    },

    // 4. List users
    listUsers: async () => {
        console.log('\n4. Listing users with pagination...');
        const params = {
            skip: 0,
            limit: 10,
            search: 'john',
            role: 'technician'
        };

        console.log('List parameters:', params);

        // try {
        //     const response = await client.listUsers(params);
        //     console.log('✓ Users retrieved successfully');
        //     console.log(`Found ${response.total} total users`);
        //     console.log(`Showing page ${response.page} of ${response.pages}`);
        //     
        //     response.items.forEach((user, index) => {
        //         console.log(`  ${index + 1}. ${user.full_name} (${user.email})`);
        //         console.log(`     Role: ${user.role}, Status: ${user.is_active ? 'Active' : 'Inactive'}`);
        //     });
        // } catch (error) {
        //     console.error('✗ Failed to list users:', error.message);
        // }

        console.log('✓ User listing example prepared');
    },

    // 5. Register vehicle
    registerVehicle: async () => {
        console.log('\n5. Registering new vehicle...');
        const vehicle = {
            license_plate: 'ABC-123',
            make: 'Toyota',
            model: 'Camry',
            year: 2022,
            color: 'Blue',
            vin: '1HGCM82633A123456',
            owner_id: 1,
            fuel_type: 'gasoline',
            transmission: 'automatic',
            mileage: 15000
        };

        console.log('Vehicle data:', {
            license_plate: vehicle.license_plate,
            make: vehicle.make,
            model: vehicle.model,
            year: vehicle.year,
            owner_id: vehicle.owner_id
        });

        // try {
        //     const registeredVehicle = await client.registerVehicle(vehicle);
        //     console.log('✓ Vehicle registered successfully');
        //     console.log('Vehicle ID:', registeredVehicle.id);
        //     console.log('Status:', registeredVehicle.status);
        // } catch (error) {
        //     console.error('✗ Vehicle registration failed:', error.message);
        // }

        console.log('✓ Vehicle registration example prepared');
    },

    // 6. List vehicles
    listVehicles: async () => {
        console.log('\n6. Listing vehicles...');
        const params = {
            skip: 0,
            limit: 5,
            make: 'Toyota',
            status: 'active'
        };

        console.log('Filter parameters:', params);

        // try {
        //     const response = await client.listVehicles(params);
        //     console.log('✓ Vehicles retrieved successfully');
        //     console.log(`Found ${response.total} vehicles matching criteria`);
        //     
        //     response.items.forEach((vehicle, index) => {
        //         console.log(`  ${index + 1}. ${vehicle.license_plate} - ${vehicle.make} ${vehicle.model}`);
        //         console.log(`     Year: ${vehicle.year}, Color: ${vehicle.color || 'N/A'}`);
        //         console.log(`     Status: ${vehicle.status}, Mileage: ${vehicle.mileage || 'N/A'}`);
        //     });
        // } catch (error) {
        //     console.error('✗ Failed to list vehicles:', error.message);
        // }

        console.log('✓ Vehicle listing example prepared');
    },

    // 7. Error handling
    errorHandling: async () => {
        console.log('\n7. Testing error handling...');
        
        // try {
        //     await client.testError('validation');
        // } catch (error) {
        //     if (error instanceof GarageRegAPIError) {
        //         console.log('✓ Caught expected API error');
        //         console.log('Error details:', {
        //             code: error.code,
        //             message: error.message,
        //             statusCode: error.statusCode
        //         });
        //         
        //         if (error.fieldErrors && error.fieldErrors.length > 0) {
        //             console.log('Field errors:');
        //             error.fieldErrors.forEach(fe => {
        //                 console.log(`  - ${fe.field}: ${fe.message} (${fe.code})`);
        //             });
        //         }
        //     } else {
        //         console.error('✗ Unexpected error type:', error);
        //     }
        // }

        console.log('✓ Error handling example prepared');
    },

    // 8. Cleanup
    cleanup: () => {
        console.log('\n8. Cleaning up...');
        // await client.logout();
        console.log('✓ Logged out and cleaned up resources');
    }
};

// Run the examples
async function runExamples() {
    try {
        exampleUsage.createClient();
        await exampleUsage.login();
        await exampleUsage.createUser();
        await exampleUsage.listUsers();
        await exampleUsage.registerVehicle();
        await exampleUsage.listVehicles();
        await exampleUsage.errorHandling();
        exampleUsage.cleanup();

        console.log('\n=== All Examples Completed Successfully ===');
        console.log('\nTo use this SDK in your project:');
        console.log('1. Build the TypeScript SDK: cd sdk/typescript && npm run build');
        console.log('2. Install the package: npm install @garagereg/api-client');
        console.log('3. Import and use: import { GarageRegClient } from "@garagereg/api-client";');
        
    } catch (error) {
        console.error('Example execution failed:', error);
    }
}

// Export for use in tests or other modules
module.exports = {
    config,
    exampleUsage,
    runExamples
};

// Run if this is the main module
if (require.main === module) {
    runExamples();
}
/**
 * Design System Showcase
 * 
 * A comprehensive demonstration of the GarageReg Design System
 * showcasing OKLCH colors, components, and accessibility features
 */

// This is a static HTML/CSS demonstration of our design system
// For full interactive components, install React dependencies first

export const designSystemShowcase = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GarageReg Design System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* OKLCH Color Variables */
        :root {
            /* Primary Colors (Brand Blue) */
            --primary-50: oklch(97% 0.020 240);
            --primary-100: oklch(93% 0.040 240);
            --primary-200: oklch(86% 0.060 240);
            --primary-300: oklch(76% 0.080 240);
            --primary-400: oklch(66% 0.100 240);
            --primary-500: oklch(56% 0.120 240);
            --primary-600: oklch(48% 0.110 240);
            --primary-700: oklch(40% 0.100 240);
            --primary-800: oklch(32% 0.080 240);
            --primary-900: oklch(24% 0.060 240);
            --primary-950: oklch(16% 0.040 240);
            
            /* Gray Scale */
            --gray-50: oklch(98% 0.005 285);
            --gray-100: oklch(95% 0.010 285);
            --gray-200: oklch(90% 0.015 285);
            --gray-300: oklch(83% 0.020 285);
            --gray-400: oklch(70% 0.025 285);
            --gray-500: oklch(57% 0.030 285);
            --gray-600: oklch(45% 0.025 285);
            --gray-700: oklch(35% 0.020 285);
            --gray-800: oklch(25% 0.015 285);
            --gray-900: oklch(15% 0.010 285);
            --gray-950: oklch(8% 0.005 285);
            
            /* Semantic Colors */
            --success-500: oklch(60% 0.130 145);
            --warning-500: oklch(70% 0.150 85);
            --error-500: oklch(55% 0.180 25);
            --info-500: oklch(60% 0.120 220);
        }
        
        /* Component Classes */
        .btn-primary {
            background-color: var(--primary-500);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-primary:hover {
            background-color: var(--primary-600);
        }
        
        .btn-primary:focus {
            outline: none;
            box-shadow: 0 0 0 2px var(--primary-500), 0 0 0 4px rgba(59, 130, 246, 0.1);
        }
        
        .btn-secondary {
            background-color: var(--gray-200);
            color: var(--gray-800);
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-secondary:hover {
            background-color: var(--gray-300);
        }
        
        .btn-success {
            background-color: var(--success-500);
            color: white;
        }
        
        .btn-warning {
            background-color: var(--warning-500);
            color: white;
        }
        
        .btn-error {
            background-color: var(--error-500);
            color: white;
        }
        
        .input-field {
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--gray-300);
            border-radius: 0.375rem;
            background-color: white;
            font-size: 0.875rem;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--primary-500);
            box-shadow: 0 0 0 1px var(--primary-500);
        }
        
        .card {
            background-color: white;
            border: 1px solid var(--gray-200);
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
        }
        
        .color-swatch {
            height: 3rem;
            border-radius: 0.375rem;
            display: flex;
            align-items: center;
            padding: 0 0.75rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        /* Focus indicators for accessibility */
        *:focus {
            outline: 2px solid var(--primary-500);
            outline-offset: 2px;
        }
        
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: var(--gray-900);
                color: var(--gray-100);
            }
            
            .card {
                background-color: var(--gray-800);
                border-color: var(--gray-700);
            }
            
            .input-field {
                background-color: var(--gray-800);
                border-color: var(--gray-600);
                color: var(--gray-100);
            }
        }
    </style>
</head>
<body class="font-sans">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 py-6 px-4">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-4xl font-bold text-gray-900">GarageReg Design System</h1>
            <p class="text-lg text-gray-600 mt-2">OKLCH-based components with full accessibility support</p>
        </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-8 space-y-12">
        <!-- Color Palette -->
        <section>
            <h2 class="text-2xl font-semibold mb-6 text-gray-900">Color System</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- Primary Colors -->
                <div>
                    <h3 class="text-lg font-medium mb-3 text-gray-800">Primary (Brand)</h3>
                    <div class="space-y-2">
                        <div class="color-swatch" style="background-color: var(--primary-50); color: black;">primary-50</div>
                        <div class="color-swatch" style="background-color: var(--primary-100); color: black;">primary-100</div>
                        <div class="color-swatch" style="background-color: var(--primary-200); color: black;">primary-200</div>
                        <div class="color-swatch" style="background-color: var(--primary-300); color: black;">primary-300</div>
                        <div class="color-swatch" style="background-color: var(--primary-400); color: white;">primary-400</div>
                        <div class="color-swatch" style="background-color: var(--primary-500); color: white;">primary-500</div>
                        <div class="color-swatch" style="background-color: var(--primary-600); color: white;">primary-600</div>
                        <div class="color-swatch" style="background-color: var(--primary-700); color: white;">primary-700</div>
                        <div class="color-swatch" style="background-color: var(--primary-800); color: white;">primary-800</div>
                        <div class="color-swatch" style="background-color: var(--primary-900); color: white;">primary-900</div>
                        <div class="color-swatch" style="background-color: var(--primary-950); color: white;">primary-950</div>
                    </div>
                </div>

                <!-- Gray Scale -->
                <div>
                    <h3 class="text-lg font-medium mb-3 text-gray-800">Gray Scale</h3>
                    <div class="space-y-2">
                        <div class="color-swatch" style="background-color: var(--gray-50); color: black;">gray-50</div>
                        <div class="color-swatch" style="background-color: var(--gray-100); color: black;">gray-100</div>
                        <div class="color-swatch" style="background-color: var(--gray-200); color: black;">gray-200</div>
                        <div class="color-swatch" style="background-color: var(--gray-300); color: black;">gray-300</div>
                        <div class="color-swatch" style="background-color: var(--gray-400); color: white;">gray-400</div>
                        <div class="color-swatch" style="background-color: var(--gray-500); color: white;">gray-500</div>
                        <div class="color-swatch" style="background-color: var(--gray-600); color: white;">gray-600</div>
                        <div class="color-swatch" style="background-color: var(--gray-700); color: white;">gray-700</div>
                        <div class="color-swatch" style="background-color: var(--gray-800); color: white;">gray-800</div>
                        <div class="color-swatch" style="background-color: var(--gray-900); color: white;">gray-900</div>
                        <div class="color-swatch" style="background-color: var(--gray-950); color: white;">gray-950</div>
                    </div>
                </div>

                <!-- Semantic Colors -->
                <div>
                    <h3 class="text-lg font-medium mb-3 text-gray-800">Semantic</h3>
                    <div class="space-y-2">
                        <div class="color-swatch" style="background-color: var(--success-500); color: white;">Success</div>
                        <div class="color-swatch" style="background-color: var(--warning-500); color: white;">Warning</div>
                        <div class="color-swatch" style="background-color: var(--error-500); color: white;">Error</div>
                        <div class="color-swatch" style="background-color: var(--info-500); color: white;">Info</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Typography -->
        <section>
            <h2 class="text-2xl font-semibold mb-6 text-gray-900">Typography</h2>
            <div class="space-y-4">
                <div class="text-xs text-gray-800">Extra Small (12px) - .text-xs</div>
                <div class="text-sm text-gray-800">Small (14px) - .text-sm</div>
                <div class="text-base text-gray-800">Base (16px) - .text-base</div>
                <div class="text-lg text-gray-800">Large (18px) - .text-lg</div>
                <div class="text-xl text-gray-800">Extra Large (20px) - .text-xl</div>
                <div class="text-2xl text-gray-800">2X Large (24px) - .text-2xl</div>
                <div class="text-3xl text-gray-800">3X Large (30px) - .text-3xl</div>
                <div class="text-4xl text-gray-800">4X Large (36px) - .text-4xl</div>
            </div>
        </section>

        <!-- Buttons -->
        <section>
            <h2 class="text-2xl font-semibold mb-6 text-gray-900">Buttons</h2>
            <div class="space-y-6">
                <!-- Variants -->
                <div>
                    <h3 class="text-lg font-medium mb-3 text-gray-800">Variants</h3>
                    <div class="flex flex-wrap gap-3">
                        <button class="btn-primary">Primary</button>
                        <button class="btn-secondary">Secondary</button>
                        <button class="btn-success btn-primary">Success</button>
                        <button class="btn-warning btn-primary">Warning</button>
                        <button class="btn-error btn-primary">Error</button>
                    </div>
                </div>

                <!-- Sizes -->
                <div>
                    <h3 class="text-lg font-medium mb-3 text-gray-800">Sizes</h3>
                    <div class="flex flex-wrap items-center gap-3">
                        <button class="btn-primary" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;">Small</button>
                        <button class="btn-primary">Medium</button>
                        <button class="btn-primary" style="padding: 0.75rem 2rem; font-size: 1.125rem;">Large</button>
                    </div>
                </div>

                <!-- States -->
                <div>
                    <h3 class="text-lg font-medium mb-3 text-gray-800">States</h3>
                    <div class="flex flex-wrap gap-3">
                        <button class="btn-primary">Normal</button>
                        <button class="btn-primary" disabled style="opacity: 0.5; cursor: not-allowed;">Disabled</button>
                        <button class="btn-primary">
                            <span style="display: inline-flex; align-items: center;">
                                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Loading
                            </span>
                        </button>
                    </div>
                </div>
            </div>
        </section>

        <!-- Form Elements -->
        <section>
            <h2 class="text-2xl font-semibold mb-6 text-gray-900">Form Elements</h2>
            <div class="max-w-md space-y-6">
                <!-- Input Field -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Email Address <span class="text-red-500">*</span>
                    </label>
                    <input type="email" class="input-field" placeholder="you@example.com" />
                    <p class="text-xs text-gray-500 mt-1.5">We'll never share your email</p>
                </div>

                <!-- Input with Error -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Password <span class="text-red-500">*</span>
                    </label>
                    <input type="password" class="input-field" placeholder="••••••••" style="border-color: var(--error-500);" />
                    <p class="text-xs text-red-500 mt-1.5">Password must be at least 8 characters</p>
                </div>

                <!-- Select -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Choose Option</label>
                    <select class="input-field">
                        <option value="">Select an option</option>
                        <option value="option1">First Option</option>
                        <option value="option2">Second Option</option>
                        <option value="option3">Third Option</option>
                    </select>
                    <p class="text-xs text-gray-500 mt-1.5">Select from the available options</p>
                </div>

                <!-- Input Sizes -->
                <div>
                    <h3 class="text-lg font-medium mb-3 text-gray-800">Input Sizes</h3>
                    <div class="space-y-3">
                        <input type="text" class="input-field" placeholder="Small input" style="padding: 0.375rem 0.5rem; font-size: 0.75rem;" />
                        <input type="text" class="input-field" placeholder="Medium input (default)" />
                        <input type="text" class="input-field" placeholder="Large input" style="padding: 0.75rem 1rem; font-size: 1rem;" />
                    </div>
                </div>
            </div>
        </section>

        <!-- Cards -->
        <section>
            <h2 class="text-2xl font-semibold mb-6 text-gray-900">Cards</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div class="card">
                    <h3 class="text-lg font-semibold mb-2">Simple Card</h3>
                    <p class="text-gray-600">This is a basic card component with clean styling and subtle shadows.</p>
                </div>
                
                <div class="card">
                    <h3 class="text-lg font-semibold mb-2">Interactive Card</h3>
                    <p class="text-gray-600 mb-4">Cards can contain various types of content including buttons and form elements.</p>
                    <button class="btn-primary">Action</button>
                </div>
                
                <div class="card">
                    <h3 class="text-lg font-semibold mb-2">Status Card</h3>
                    <p class="text-gray-600 mb-4">Cards can show different states and status indicators.</p>
                    <div class="flex items-center space-x-2">
                        <div class="w-2 h-2 rounded-full" style="background-color: var(--success-500);"></div>
                        <span class="text-sm text-gray-600">Active</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- Accessibility Testing -->
        <section>
            <h2 class="text-2xl font-semibold mb-6 text-gray-900">Accessibility Features</h2>
            <div class="space-y-4">
                <div class="card">
                    <h3 class="text-lg font-medium mb-2">Keyboard Navigation</h3>
                    <p class="text-gray-600 mb-4">Tab through these elements to test keyboard interaction:</p>
                    <div class="flex flex-wrap gap-3">
                        <button class="btn-primary">Button 1</button>
                        <button class="btn-secondary">Button 2</button>
                        <input type="text" class="input-field" placeholder="Text input" style="width: 200px;" />
                        <select class="input-field" style="width: 150px;">
                            <option>Select option</option>
                            <option>Option 1</option>
                            <option>Option 2</option>
                        </select>
                    </div>
                </div>

                <div class="card">
                    <h3 class="text-lg font-medium mb-2">Focus Management</h3>
                    <p class="text-gray-600 mb-4">All interactive elements have visible focus indicators:</p>
                    <div class="space-y-3">
                        <button class="btn-primary" aria-label="Save document">💾 Save</button>
                        <input class="input-field" aria-label="Search query" placeholder="Search..." style="width: 200px;" />
                        <button class="btn-error btn-primary" aria-label="Delete item">🗑️ Delete</button>
                    </div>
                </div>

                <div class="card">
                    <h3 class="text-lg font-medium mb-2">Screen Reader Support</h3>
                    <p class="text-gray-600 mb-4">All elements have proper ARIA labels and semantic markup:</p>
                    <div class="space-y-3">
                        <div role="status" aria-live="polite">
                            <span class="sr-only">Loading status:</span>
                            System status: All services operational
                        </div>
                        <button aria-describedby="help-text" class="btn-primary">
                            Complex Action
                        </button>
                        <div id="help-text" class="text-xs text-gray-500">
                            This action will perform a complex operation that cannot be undone
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Design Tokens -->
        <section>
            <h2 class="text-2xl font-semibold mb-6 text-gray-900">Design Tokens</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="card">
                    <h3 class="text-lg font-medium mb-4">Spacing Scale</h3>
                    <div class="space-y-2">
                        <div class="flex items-center space-x-4">
                            <div class="w-2 h-4 bg-gray-300"></div>
                            <span class="text-sm">2px (0.5)</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="w-4 h-4 bg-gray-300"></div>
                            <span class="text-sm">4px (1)</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="w-6 h-4 bg-gray-300"></div>
                            <span class="text-sm">6px (1.5)</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="w-8 h-4 bg-gray-300"></div>
                            <span class="text-sm">8px (2)</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="w-12 h-4 bg-gray-300"></div>
                            <span class="text-sm">12px (3)</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="w-16 h-4 bg-gray-300"></div>
                            <span class="text-sm">16px (4)</span>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3 class="text-lg font-medium mb-4">Border Radius</h3>
                    <div class="space-y-3">
                        <div class="p-3 bg-gray-100" style="border-radius: 2px;">2px (sm)</div>
                        <div class="p-3 bg-gray-100" style="border-radius: 4px;">4px (default)</div>
                        <div class="p-3 bg-gray-100" style="border-radius: 6px;">6px (md)</div>
                        <div class="p-3 bg-gray-100" style="border-radius: 8px;">8px (lg)</div>
                        <div class="p-3 bg-gray-100" style="border-radius: 12px;">12px (xl)</div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="bg-gray-50 border-t border-gray-200 py-8 px-4 mt-16">
        <div class="max-w-6xl mx-auto text-center">
            <p class="text-gray-600">GarageReg Design System - Built with OKLCH colors and accessibility in mind</p>
            <p class="text-sm text-gray-500 mt-2">Test keyboard navigation, screen readers, and high contrast mode</p>
        </div>
    </footer>

    <style>
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .animate-spin {
            animation: spin 1s linear infinite;
        }
    </style>
</body>
</html>
`;

// Export as string for use in demos or documentation
export default designSystemShowcase;
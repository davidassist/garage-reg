import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: ["class"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Border and Ring colors
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        
        // Background colors
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        
        // Primary colors (OKLCH Blue)
        primary: {
          50: "oklch(97% 0.020 240)",
          100: "oklch(93% 0.040 240)",
          200: "oklch(86% 0.060 240)",
          300: "oklch(76% 0.080 240)",
          400: "oklch(66% 0.100 240)",
          500: "oklch(56% 0.120 240)",  // Main brand color
          600: "oklch(48% 0.110 240)",
          700: "oklch(40% 0.100 240)",
          800: "oklch(32% 0.080 240)",
          900: "oklch(24% 0.060 240)",
          950: "oklch(16% 0.040 240)",
          DEFAULT: "oklch(var(--primary))",
          foreground: "oklch(var(--primary-foreground))",
        },
        
        // Secondary/Gray colors (OKLCH Neutral)
        secondary: {
          50: "oklch(98% 0.005 285)",
          100: "oklch(95% 0.010 285)",
          200: "oklch(90% 0.015 285)",
          300: "oklch(83% 0.020 285)",
          400: "oklch(70% 0.025 285)",
          500: "oklch(57% 0.030 285)",  // True gray
          600: "oklch(45% 0.025 285)",
          700: "oklch(35% 0.020 285)",
          800: "oklch(25% 0.015 285)",
          900: "oklch(15% 0.010 285)",
          950: "oklch(8% 0.005 285)",
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        
        // Semantic colors (OKLCH)
        success: {
          50: "oklch(95% 0.040 145)",
          100: "oklch(90% 0.060 145)",
          200: "oklch(83% 0.080 145)",
          300: "oklch(75% 0.100 145)",
          400: "oklch(68% 0.115 145)",
          500: "oklch(60% 0.130 145)",  // Main success
          600: "oklch(52% 0.120 145)",
          700: "oklch(44% 0.110 145)",
          800: "oklch(36% 0.090 145)",
          900: "oklch(28% 0.070 145)",
          950: "oklch(20% 0.050 145)",
        },
        
        warning: {
          50: "oklch(96% 0.040 85)",
          100: "oklch(92% 0.070 85)",
          200: "oklch(87% 0.100 85)",
          300: "oklch(81% 0.125 85)",
          400: "oklch(76% 0.140 85)",
          500: "oklch(70% 0.150 85)",   // Main warning
          600: "oklch(63% 0.140 85)",
          700: "oklch(55% 0.130 85)",
          800: "oklch(46% 0.110 85)",
          900: "oklch(38% 0.090 85)",
          950: "oklch(30% 0.070 85)",
        },
        
        error: {
          50: "oklch(95% 0.040 25)",
          100: "oklch(90% 0.070 25)",
          200: "oklch(84% 0.100 25)",
          300: "oklch(76% 0.130 25)",
          400: "oklch(68% 0.150 25)",
          500: "oklch(55% 0.180 25)",   // Main error
          600: "oklch(48% 0.170 25)",
          700: "oklch(41% 0.150 25)",
          800: "oklch(34% 0.130 25)",
          900: "oklch(27% 0.100 25)",
          950: "oklch(20% 0.080 25)",
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        
        info: {
          50: "oklch(96% 0.030 220)",
          100: "oklch(92% 0.050 220)",
          200: "oklch(86% 0.070 220)",
          300: "oklch(78% 0.090 220)",
          400: "oklch(69% 0.105 220)",
          500: "oklch(60% 0.120 220)",  // Main info
          600: "oklch(52% 0.110 220)",
          700: "oklch(44% 0.100 220)",
          800: "oklch(36% 0.080 220)",
          900: "oklch(28% 0.060 220)",
          950: "oklch(20% 0.040 220)",
        },
        
        // Additional semantic colors for shadcn/ui compatibility
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        
        // Aliases for common usage
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
      },
      
      borderRadius: {
        xl: "calc(var(--radius) + 4px)",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular"],
      },
      
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
        xl: ["1.25rem", { lineHeight: "1.75rem" }],
        "2xl": ["1.5rem", { lineHeight: "2rem" }],
        "3xl": ["1.875rem", { lineHeight: "2.25rem" }],
        "4xl": ["2.25rem", { lineHeight: "2.5rem" }],
        "5xl": ["3rem", { lineHeight: "1" }],
        "6xl": ["3.75rem", { lineHeight: "1" }],
      },
      
      spacing: {
        "0.5": "0.125rem",  // 2px
        "1.5": "0.375rem",  // 6px
        "2.5": "0.625rem",  // 10px
        "3.5": "0.875rem",  // 14px
      },
      
      boxShadow: {
        xs: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
        sm: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        DEFAULT: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
        md: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
        lg: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
        xl: "0 25px 50px -12px rgb(0 0 0 / 0.25)",
        "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
        inner: "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
        none: "none",
      },
      
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
        "slide-in-from-top": "slide-in-from-top 0.2s ease-out",
        "slide-in-from-bottom": "slide-in-from-bottom 0.2s ease-out",
        "slide-in-from-left": "slide-in-from-left 0.2s ease-out",
        "slide-in-from-right": "slide-in-from-right 0.2s ease-out",
      },
      
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-in-from-top": {
          from: { transform: "translateY(-100%)" },
          to: { transform: "translateY(0)" },
        },
        "slide-in-from-bottom": {
          from: { transform: "translateY(100%)" },
          to: { transform: "translateY(0)" },
        },
        "slide-in-from-left": {
          from: { transform: "translateX(-100%)" },
          to: { transform: "translateX(0)" },
        },
        "slide-in-from-right": {
          from: { transform: "translateX(100%)" },
          to: { transform: "translateX(0)" },
        },
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
} satisfies Config

export default config
import { fontFamily } from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
const config = {
	darkMode: ["class"],
	content: ["./src/**/*.{html,js,svelte,ts}"],
	safelist: ["dark"],
	theme: {
		container: {
			center: true,
			padding: "2rem",
			screens: {
				"2xl": "1400px"
			}
		},
		extend: {
			colors: {
				border: "hsl(var(--border) / <alpha-value>)",
				input: "hsl(var(--input) / <alpha-value>)",
				ring: "hsl(var(--ring) / <alpha-value>)",
				background: "hsl(var(--background) / <alpha-value>)",
				foreground: "hsl(var(--foreground) / <alpha-value>)",
				primary: {
					DEFAULT: "hsl(var(--primary) / <alpha-value>)",
					foreground: "hsl(var(--primary-foreground) / <alpha-value>)"
				},
				secondary: {
					DEFAULT: "hsl(var(--secondary) / <alpha-value>)",
					foreground: "hsl(var(--secondary-foreground) / <alpha-value>)"
				},
				destructive: {
					DEFAULT: "hsl(var(--destructive) / <alpha-value>)",
					foreground: "hsl(var(--destructive-foreground) / <alpha-value>)"
				},
				muted: {
					DEFAULT: "hsl(var(--muted) / <alpha-value>)",
					foreground: "hsl(var(--muted-foreground) / <alpha-value>)"
				},
				accent: {
					DEFAULT: "hsl(var(--accent) / <alpha-value>)",
					foreground: "hsl(var(--accent-foreground) / <alpha-value>)"
				},
				popover: {
					DEFAULT: "hsl(var(--popover) / <alpha-value>)",
					foreground: "hsl(var(--popover-foreground) / <alpha-value>)"
				},
				card: {
					DEFAULT: "hsl(var(--card) / <alpha-value>)",
					foreground: "hsl(var(--card-foreground) / <alpha-value>)"
				},
				// Voxelle brand colors
				vx: {
					cyan: "hsl(var(--vx-cyan) / <alpha-value>)",
					purple: "hsl(var(--vx-purple) / <alpha-value>)",
					pink: "hsl(var(--vx-pink) / <alpha-value>)",
					emerald: "hsl(var(--vx-emerald) / <alpha-value>)",
					amber: "hsl(var(--vx-amber) / <alpha-value>)",
					red: "hsl(var(--vx-red) / <alpha-value>)"
				}
			},
			borderRadius: {
				lg: "var(--radius)",
				md: "calc(var(--radius) - 2px)",
				sm: "calc(var(--radius) - 4px)",
				xl: "calc(var(--radius) + 4px)",
				"2xl": "calc(var(--radius) + 8px)",
				"3xl": "calc(var(--radius) + 12px)"
			},
			fontFamily: {
				sans: ["Inter", ...fontFamily.sans],
				display: ["Space Grotesk", "Inter", ...fontFamily.sans],
				mono: ["JetBrains Mono", ...fontFamily.mono]
			},
			animation: {
				"pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
				"pulse-glow": "pulse-glow 2s ease-in-out infinite",
				"float": "float 6s ease-in-out infinite",
				"gradient-flow": "gradient-flow 8s ease infinite",
				"border-rotate": "border-rotate 4s linear infinite",
				"fade-in": "fade-in 0.5s ease-out",
				"slide-up": "slide-up 0.5s ease-out",
				"slide-down": "slide-down 0.3s ease-out",
				"scale-in": "scale-in 0.2s ease-out"
			},
			keyframes: {
				"pulse-glow": {
					"0%, 100%": { opacity: "1", transform: "scale(1)" },
					"50%": { opacity: "0.5", transform: "scale(1.05)" }
				},
				"float": {
					"0%, 100%": { transform: "translateY(0)" },
					"50%": { transform: "translateY(-10px)" }
				},
				"gradient-flow": {
					"0%, 100%": { backgroundPosition: "0% 50%" },
					"50%": { backgroundPosition: "100% 50%" }
				},
				"border-rotate": {
					"0%": { backgroundPosition: "0% 0%" },
					"100%": { backgroundPosition: "300% 300%" }
				},
				"fade-in": {
					"0%": { opacity: "0" },
					"100%": { opacity: "1" }
				},
				"slide-up": {
					"0%": { opacity: "0", transform: "translateY(10px)" },
					"100%": { opacity: "1", transform: "translateY(0)" }
				},
				"slide-down": {
					"0%": { opacity: "0", transform: "translateY(-10px)" },
					"100%": { opacity: "1", transform: "translateY(0)" }
				},
				"scale-in": {
					"0%": { opacity: "0", transform: "scale(0.95)" },
					"100%": { opacity: "1", transform: "scale(1)" }
				}
			},
			backdropBlur: {
				xs: "2px"
			},
			boxShadow: {
				"glow-sm": "0 0 10px var(--tw-shadow-color)",
				"glow-md": "0 0 20px var(--tw-shadow-color)",
				"glow-lg": "0 0 40px var(--tw-shadow-color)",
				"glow-xl": "0 0 60px var(--tw-shadow-color)",
				"inner-glow": "inset 0 0 20px var(--tw-shadow-color)"
			}
		}
	}
};

export default config;

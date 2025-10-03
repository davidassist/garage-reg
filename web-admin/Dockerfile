# Multi-stage Dockerfile for Next.js web admin

# =============================================================================
# Dependencies stage
# =============================================================================
FROM node:18-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# =============================================================================
# Builder stage
# =============================================================================
FROM node:18-alpine AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set environment for build
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

# Build application
RUN npm run build

# =============================================================================
# Development stage
# =============================================================================
FROM node:18-alpine AS development
WORKDIR /app

# Install dependencies including dev dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Create app user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV development
ENV NEXT_TELEMETRY_DISABLED 1

# Start development server
CMD ["npm", "run", "dev"]

# =============================================================================
# Production runner stage
# =============================================================================
FROM node:18-alpine AS runner
WORKDIR /app

# Set environment
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create app user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# Expose port
EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start production server
CMD ["node", "server.js"]
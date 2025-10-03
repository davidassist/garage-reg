#!/bin/bash
# =============================================================================
# TLS CERTIFICATE GENERATOR FOR LOCAL DEVELOPMENT
# Creates self-signed certificates for garagereg.local domains
# =============================================================================

set -euo pipefail

# Configuration
CERT_DIR="$(dirname "$0")/certs"
DOMAIN="garagereg.local"
WILDCARD_DOMAIN="*.garagereg.local"
KEY_SIZE=2048
DAYS=365

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create certificate directory
log_info "Creating certificate directory: $CERT_DIR"
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

# Generate private key for CA
log_info "Generating CA private key..."
if [ ! -f "ca.key" ]; then
    openssl genrsa -out ca.key 4096
    log_success "CA private key generated"
else
    log_warning "CA private key already exists"
fi

# Generate CA certificate
log_info "Generating CA certificate..."
if [ ! -f "ca.crt" ]; then
    cat > ca.conf << EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
C = HU
ST = Budapest
L = Budapest
O = GarageReg Local Development
OU = IT Department
CN = GarageReg Local CA

[v3_ca]
basicConstraints = critical, CA:TRUE
keyUsage = critical, digitalSignature, keyEncipherment, keyCertSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always, issuer:always
EOF

    openssl req -new -x509 -days $DAYS -key ca.key -out ca.crt -config ca.conf
    log_success "CA certificate generated"
else
    log_warning "CA certificate already exists"
fi

# Generate private key for garagereg.local
log_info "Generating private key for $DOMAIN..."
if [ ! -f "garagereg.local.key" ]; then
    openssl genrsa -out garagereg.local.key $KEY_SIZE
    log_success "Private key for $DOMAIN generated"
else
    log_warning "Private key for $DOMAIN already exists"
fi

# Generate certificate signing request
log_info "Generating certificate signing request for $DOMAIN..."
cat > garagereg.local.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = HU
ST = Budapest
L = Budapest
O = GarageReg Local Development
OU = IT Department
CN = garagereg.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = garagereg.local
DNS.2 = *.garagereg.local
DNS.3 = api.garagereg.local
DNS.4 = admin.garagereg.local
DNS.5 = app.garagereg.local
DNS.6 = traefik.garagereg.local
DNS.7 = mail.garagereg.local
DNS.8 = metrics.garagereg.local
DNS.9 = dashboard.garagereg.local
DNS.10 = mobile-api.garagereg.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

openssl req -new -key garagereg.local.key -out garagereg.local.csr -config garagereg.local.conf

# Generate certificate signed by CA
log_info "Generating certificate for $DOMAIN signed by CA..."
cat > garagereg.local.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = garagereg.local
DNS.2 = *.garagereg.local
DNS.3 = api.garagereg.local
DNS.4 = admin.garagereg.local
DNS.5 = app.garagereg.local
DNS.6 = traefik.garagereg.local
DNS.7 = mail.garagereg.local
DNS.8 = metrics.garagereg.local
DNS.9 = dashboard.garagereg.local
DNS.10 = mobile-api.garagereg.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

openssl x509 -req -in garagereg.local.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out garagereg.local.crt -days $DAYS -extensions v3_req -extfile garagereg.local.ext

log_success "Certificate for $DOMAIN generated"

# Generate wildcard certificate
log_info "Generating wildcard certificate for $WILDCARD_DOMAIN..."
if [ ! -f "wildcard.garagereg.local.key" ]; then
    openssl genrsa -out wildcard.garagereg.local.key $KEY_SIZE
fi

cat > wildcard.garagereg.local.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = HU
ST = Budapest
L = Budapest
O = GarageReg Local Development
OU = IT Department
CN = *.garagereg.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.garagereg.local
DNS.2 = garagereg.local
EOF

openssl req -new -key wildcard.garagereg.local.key -out wildcard.garagereg.local.csr -config wildcard.garagereg.local.conf

cat > wildcard.garagereg.local.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.garagereg.local
DNS.2 = garagereg.local
EOF

openssl x509 -req -in wildcard.garagereg.local.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out wildcard.garagereg.local.crt -days $DAYS -extensions v3_req -extfile wildcard.garagereg.local.ext

log_success "Wildcard certificate generated"

# Set proper permissions
chmod 600 *.key
chmod 644 *.crt

# Verify certificates
log_info "Verifying generated certificates..."
echo ""
echo "=== CA Certificate ==="
openssl x509 -in ca.crt -text -noout | grep -E "(Subject:|Validity|DNS:|IP:)"
echo ""
echo "=== Domain Certificate ==="
openssl x509 -in garagereg.local.crt -text -noout | grep -E "(Subject:|Validity|DNS:|IP:)"
echo ""
echo "=== Wildcard Certificate ==="
openssl x509 -in wildcard.garagereg.local.crt -text -noout | grep -E "(Subject:|Validity|DNS:|IP:)"

# Test certificate validity
log_info "Testing certificate validity..."
if openssl verify -CAfile ca.crt garagereg.local.crt; then
    log_success "Domain certificate is valid"
else
    log_error "Domain certificate validation failed"
    exit 1
fi

if openssl verify -CAfile ca.crt wildcard.garagereg.local.crt; then
    log_success "Wildcard certificate is valid"
else
    log_error "Wildcard certificate validation failed" 
    exit 1
fi

# Cleanup temporary files
log_info "Cleaning up temporary files..."
rm -f *.csr *.conf *.ext *.srl

# Create certificate bundle
log_info "Creating certificate bundle..."
cat ca.crt garagereg.local.crt > garagereg.local.bundle.crt
cat ca.crt wildcard.garagereg.local.crt > wildcard.garagereg.local.bundle.crt

# Generate summary
cat > certificate-info.txt << EOF
=============================================================================
GARAGEREG LOCAL DEVELOPMENT CERTIFICATES
Generated on: $(date)
=============================================================================

CERTIFICATE AUTHORITY (CA):
- File: ca.crt
- Key: ca.key
- Valid for: $DAYS days from $(date)

DOMAIN CERTIFICATE:
- Domain: garagereg.local
- File: garagereg.local.crt
- Key: garagereg.local.key
- Bundle: garagereg.local.bundle.crt
- Valid for: $DAYS days from $(date)
- Subject Alternative Names:
  - garagereg.local
  - *.garagereg.local
  - api.garagereg.local
  - admin.garagereg.local
  - app.garagereg.local
  - traefik.garagereg.local
  - mail.garagereg.local
  - metrics.garagereg.local
  - dashboard.garagereg.local
  - mobile-api.garagereg.local

WILDCARD CERTIFICATE:
- Domain: *.garagereg.local
- File: wildcard.garagereg.local.crt
- Key: wildcard.garagereg.local.key
- Bundle: wildcard.garagereg.local.bundle.crt
- Valid for: $DAYS days from $(date)

INSTALLATION INSTRUCTIONS:

1. Trust the CA certificate in your system:
   - Windows: Import ca.crt to "Trusted Root Certification Authorities"
   - macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ca.crt
   - Linux: sudo cp ca.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates

2. Add domains to your hosts file (/etc/hosts or C:\Windows\System32\drivers\etc\hosts):
   127.0.0.1 garagereg.local
   127.0.0.1 api.garagereg.local
   127.0.0.1 admin.garagereg.local
   127.0.0.1 app.garagereg.local
   127.0.0.1 traefik.garagereg.local
   127.0.0.1 mail.garagereg.local
   127.0.0.1 metrics.garagereg.local
   127.0.0.1 dashboard.garagereg.local
   127.0.0.1 mobile-api.garagereg.local

3. Start the development environment:
   docker compose -f infra/docker-compose.yml up

4. Access services:
   - Admin Interface: https://admin.garagereg.local
   - API Documentation: https://api.garagereg.local/docs
   - Traefik Dashboard: https://traefik.garagereg.local (admin:admin)
   - Mail Testing: https://mail.garagereg.local
   - Metrics: https://metrics.garagereg.local
   - Grafana Dashboard: https://dashboard.garagereg.local

=============================================================================
EOF

log_success "Certificate generation completed!"
log_info "Certificate information saved to certificate-info.txt"
log_info "Next steps:"
echo "  1. Trust the CA certificate (ca.crt) in your system"
echo "  2. Add domains to your hosts file"
echo "  3. Run: docker compose -f infra/docker-compose.yml up"

echo ""
log_warning "Remember to keep the private keys secure!"
log_warning "These certificates are for LOCAL DEVELOPMENT ONLY!"
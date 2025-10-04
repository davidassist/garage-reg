# =============================================================================
# TLS CERTIFICATE GENERATOR FOR LOCAL DEVELOPMENT (PowerShell)
# Creates self-signed certificates for garagereg.local domains
# =============================================================================

param(
    [string]$CertDir = "$PSScriptRoot\certs",
    [string]$Domain = "garagereg.local",
    [int]$Days = 365
)

# Colors for output
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Check if OpenSSL is available
try {
    $null = Get-Command openssl -ErrorAction Stop
    Write-Info "OpenSSL found in PATH"
} catch {
    Write-Error "OpenSSL not found in PATH. Please install OpenSSL."
    Write-Info "You can install OpenSSL via:"
    Write-Info "  - Chocolatey: choco install openssl"
    Write-Info "  - Scoop: scoop install openssl"
    Write-Info "  - Download from https://slproweb.com/products/Win32OpenSSL.html"
    exit 1
}

# Create certificate directory
Write-Info "Creating certificate directory: $CertDir"
if (!(Test-Path $CertDir)) {
    New-Item -ItemType Directory -Path $CertDir -Force | Out-Null
}
Set-Location $CertDir

# Generate private key for CA
Write-Info "Generating CA private key..."
if (!(Test-Path "ca.key")) {
    & openssl genrsa -out ca.key 4096 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "CA private key generated"
    } else {
        Write-Error "Failed to generate CA private key"
        exit 1
    }
} else {
    Write-Warning "CA private key already exists"
}

# Generate CA certificate configuration
$caConf = @"
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
C=HU
ST=Budapest
L=Budapest
O=GarageReg Local Development
OU=Development Team
CN=GarageReg Local CA
emailAddress=dev@garagereg.local

[v3_ca]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints=critical,CA:true
keyUsage=critical,digitalSignature,cRLSign,keyCertSign
"@

$caConf | Out-File -Encoding UTF8 "ca.conf"

# Generate CA certificate
Write-Info "Generating CA certificate..."
if (!(Test-Path "ca.crt")) {
    & openssl req -new -x509 -days $Days -key ca.key -out ca.crt -config ca.conf 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "CA certificate generated"
    } else {
        Write-Error "Failed to generate CA certificate"
        exit 1
    }
} else {
    Write-Warning "CA certificate already exists"
}

# Generate domain private key
Write-Info "Generating domain private key..."
if (!(Test-Path "domain.key")) {
    & openssl genrsa -out domain.key 2048 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Domain private key generated"
    } else {
        Write-Error "Failed to generate domain private key"
        exit 1
    }
} else {
    Write-Warning "Domain private key already exists"
}

# Generate domain certificate configuration
$domainConf = @"
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C=HU
ST=Budapest
L=Budapest
O=GarageReg Local Development
OU=Development Team
CN=$Domain
emailAddress=dev@garagereg.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $Domain
DNS.2 = *.$Domain
DNS.3 = localhost
DNS.4 = api.$Domain
DNS.5 = admin.$Domain
DNS.6 = app.$Domain
DNS.7 = traefik.$Domain
DNS.8 = mail.$Domain
DNS.9 = metrics.$Domain
DNS.10 = dashboard.$Domain
DNS.11 = mobile-api.$Domain
IP.1 = 127.0.0.1
IP.2 = ::1
"@

$domainConf | Out-File -Encoding UTF8 "domain.conf"

# Generate certificate signing request
Write-Info "Generating certificate signing request..."
& openssl req -new -key domain.key -out domain.csr -config domain.conf 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Certificate signing request generated"
} else {
    Write-Error "Failed to generate certificate signing request"
    exit 1
}

# Generate domain certificate
Write-Info "Generating domain certificate..."
& openssl x509 -req -in domain.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out domain.crt -days $Days -extensions v3_req -extfile domain.conf 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Domain certificate generated"
} else {
    Write-Error "Failed to generate domain certificate"
    exit 1
}

# Create certificate bundle
Write-Info "Creating certificate bundle..."
Get-Content "domain.crt", "ca.crt" | Set-Content "fullchain.pem"
Copy-Item "domain.key" "privkey.pem"

Write-Success "All certificates generated successfully!"
Write-Info ""
Write-Info "Generated files:"
Write-Info "  - ca.crt (Certificate Authority)"
Write-Info "  - ca.key (CA Private Key)"
Write-Info "  - domain.crt (Domain Certificate)"
Write-Info "  - domain.key (Domain Private Key)"
Write-Info "  - fullchain.pem (Full Certificate Chain)"
Write-Info "  - privkey.pem (Private Key for Traefik)"
Write-Info ""
Write-Warning "IMPORTANT: Trust the CA certificate in your browser!"
Write-Info ""
Write-Info "To trust the CA certificate:"
Write-Info "1. Open 'ca.crt' file"
Write-Info "2. Click 'Install Certificate...'"
Write-Info "3. Select 'Local Machine' and click 'Next'"
Write-Info "4. Select 'Place all certificates in the following store'"
Write-Info "5. Click 'Browse...' and select 'Trusted Root Certification Authorities'"
Write-Info "6. Click 'OK', then 'Next', then 'Finish'"
Write-Info ""
Write-Info "Add these entries to your hosts file (C:\Windows\System32\drivers\etc\hosts):"
Write-Info ""
@"
127.0.0.1 garagereg.local
127.0.0.1 api.garagereg.local
127.0.0.1 admin.garagereg.local
127.0.0.1 app.garagereg.local
127.0.0.1 traefik.garagereg.local
127.0.0.1 mail.garagereg.local
127.0.0.1 metrics.garagereg.local
127.0.0.1 dashboard.garagereg.local
127.0.0.1 mobile-api.garagereg.local
"@ | Write-Host -ForegroundColor Cyan

Write-Info ""
Write-Success "Certificate generation completed! 🎉"
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Trust the CA certificate (see instructions above)"
Write-Info "2. Add hosts entries (see above)"
Write-Info "3. Start the development environment:"
Write-Info "   docker compose -f infra/docker-compose.yml up"
Write-Info ""
Write-Info "4. Access services:"
Write-Info "   - Admin Interface: https://admin.garagereg.local"
Write-Info "   - API Documentation: https://api.garagereg.local/docs"
Write-Info "   - Traefik Dashboard: https://traefik.garagereg.local (admin:admin)"
Write-Info "   - Mail Testing: https://mail.garagereg.local"
Write-Info "   - Metrics: https://metrics.garagereg.local (admin:admin)"
Write-Info "   - Dashboard: https://dashboard.garagereg.local (admin:admin)"
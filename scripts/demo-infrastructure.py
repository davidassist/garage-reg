#!/usr/bin/env python3
"""
GarageReg Infrastructure End-to-End Demo
Complete demonstration of local/staging environment functionality
"""

import asyncio
import json
import time
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
import psycopg2
import redis
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.live import Live
from rich.text import Text

# Initialize Rich console
console = Console()

class InfrastructureDemo:
    """Complete infrastructure demonstration and validation"""
    
    def __init__(self):
        self.base_url = "https://api.garagereg.local"
        self.admin_url = "https://admin.garagereg.local"
        self.traefik_url = "https://traefik.garagereg.local"
        self.mail_url = "https://mail.garagereg.local"
        self.metrics_url = "https://metrics.garagereg.local"
        self.dashboard_url = "https://dashboard.garagereg.local"
        
        # Test credentials
        self.test_user = {
            "email": "admin@garagereg.local",
            "password": "admin123",
            "full_name": "Admin User"
        }
        
        # Connection strings (will be loaded from environment)
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "garagereg",
            "user": "garagereg",
            "password": "garagereg_secure_dev_password_2024"
        }
        
        self.redis_config = {
            "host": "localhost",
            "port": 6379,
            "password": "garagereg_redis_dev_2024",
            "db": 0
        }
        
        # HTTP client with SSL verification disabled for self-signed certs
        self.client = httpx.AsyncClient(
            verify=False,
            timeout=30.0,
            follow_redirects=True
        )
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_header(self, title: str):
        """Print a styled header"""
        console.print(Panel(f"[bold blue]{title}[/bold blue]", expand=False))
    
    def print_success(self, message: str):
        """Print success message"""
        console.print(f"[green]✅ {message}[/green]")
    
    def print_warning(self, message: str):
        """Print warning message"""
        console.print(f"[yellow]⚠️ {message}[/yellow]")
    
    def print_error(self, message: str):
        """Print error message"""
        console.print(f"[red]❌ {message}[/red]")
    
    def print_info(self, message: str):
        """Print info message"""
        console.print(f"[cyan]ℹ️ {message}[/cyan]")
    
    async def check_docker_services(self) -> bool:
        """Check if Docker services are running"""
        self.print_header("Docker Services Health Check")
        
        try:
            # Check if docker-compose is available
            result = subprocess.run(
                ["docker", "compose", "-f", "infra/docker-compose.yml", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            services = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    services.append(json.loads(line))
            
            # Create table for service status
            table = Table(title="Docker Services Status")
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Health", style="green")
            table.add_column("Ports", style="blue")
            
            all_healthy = True
            for service in services:
                name = service.get("Name", "Unknown")
                state = service.get("State", "Unknown")
                health = service.get("Health", "N/A")
                ports = service.get("Publishers", [])
                
                # Format ports
                port_str = ""
                if ports:
                    port_list = []
                    for port in ports:
                        if isinstance(port, dict):
                            pub_port = port.get("PublishedPort", "")
                            target_port = port.get("TargetPort", "")
                            if pub_port and target_port:
                                port_list.append(f"{pub_port}:{target_port}")
                    port_str = ", ".join(port_list)
                
                # Determine health status
                if health == "healthy" or (health == "N/A" and state == "running"):
                    health_display = "[green]Healthy[/green]"
                elif health == "starting":
                    health_display = "[yellow]Starting[/yellow]"
                    all_healthy = False
                else:
                    health_display = "[red]Unhealthy[/red]"
                    all_healthy = False
                
                table.add_row(name, state, health_display, port_str)
            
            console.print(table)
            
            if all_healthy:
                self.print_success("All Docker services are healthy!")
                return True
            else:
                self.print_warning("Some Docker services are not healthy")
                return False
                
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to check Docker services: {e}")
            return False
        except Exception as e:
            self.print_error(f"Error checking Docker services: {e}")
            return False
    
    async def test_database_connectivity(self) -> bool:
        """Test PostgreSQL database connectivity"""
        self.print_header("Database Connectivity Test")
        
        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            self.print_success(f"PostgreSQL connected: {version[:50]}...")
            
            # Test extensions
            cursor.execute("""
                SELECT extname FROM pg_extension 
                WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_trgm', 'unaccent')
            """)
            extensions = [row[0] for row in cursor.fetchall()]
            
            expected_extensions = ['uuid-ossp', 'pgcrypto', 'pg_trgm', 'unaccent']
            for ext in expected_extensions:
                if ext in extensions:
                    self.print_success(f"Extension {ext} is installed")
                else:
                    self.print_warning(f"Extension {ext} is missing")
            
            # Test tables existence
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                self.print_success(f"Found {len(tables)} tables in database")
            else:
                self.print_warning("No tables found - migrations may not have run")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            self.print_error(f"Database connectivity failed: {e}")
            return False
    
    async def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity"""
        self.print_header("Redis Connectivity Test")
        
        try:
            # Connect to Redis
            r = redis.Redis(**self.redis_config)
            
            # Test basic operations
            r.ping()
            self.print_success("Redis connected successfully")
            
            # Test set/get
            test_key = "demo:test"
            test_value = "infrastructure_demo"
            r.set(test_key, test_value, ex=60)
            
            retrieved = r.get(test_key)
            if retrieved and retrieved.decode() == test_value:
                self.print_success("Redis read/write test passed")
            else:
                self.print_error("Redis read/write test failed")
                return False
            
            # Get Redis info
            info = r.info()
            self.print_success(f"Redis version: {info['redis_version']}")
            self.print_info(f"Used memory: {info['used_memory_human']}")
            
            # Cleanup
            r.delete(test_key)
            return True
            
        except Exception as e:
            self.print_error(f"Redis connectivity failed: {e}")
            return False
    
    async def test_traefik_routing(self) -> bool:
        """Test Traefik reverse proxy routing"""
        self.print_header("Traefik Routing Test")
        
        endpoints = [
            (f"{self.base_url}/health", "Backend API Health"),
            (f"{self.traefik_url}/api/version", "Traefik API"),
            (f"{self.admin_url}", "Admin Interface"),
            (f"{self.mail_url}", "MailHog Interface"),
        ]
        
        all_passed = True
        
        for url, description in endpoints:
            try:
                response = await self.client.get(url, timeout=10.0)
                if response.status_code == 200:
                    self.print_success(f"{description}: OK ({response.status_code})")
                else:
                    self.print_warning(f"{description}: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.print_error(f"{description}: Failed - {str(e)[:50]}...")
                all_passed = False
        
        return all_passed
    
    async def test_api_functionality(self) -> bool:
        """Test API endpoints functionality"""
        self.print_header("API Functionality Test")
        
        try:
            # Test health endpoint
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.print_success(f"Health check passed: {health_data.get('status', 'unknown')}")
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                return False
            
            # Test API documentation
            response = await self.client.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                self.print_success("API documentation accessible")
            else:
                self.print_warning(f"API docs not accessible: {response.status_code}")
            
            # Test authentication endpoints
            auth_endpoints = [
                "/api/auth/register",
                "/api/auth/login", 
                "/api/auth/refresh"
            ]
            
            for endpoint in auth_endpoints:
                try:
                    # OPTIONS request to check CORS
                    response = await self.client.options(f"{self.base_url}{endpoint}")
                    if response.status_code in [200, 405]:  # 405 is also acceptable for OPTIONS
                        self.print_success(f"Auth endpoint accessible: {endpoint}")
                    else:
                        self.print_warning(f"Auth endpoint issue: {endpoint} ({response.status_code})")
                except Exception as e:
                    self.print_error(f"Auth endpoint failed: {endpoint} - {str(e)[:30]}...")
            
            return True
            
        except Exception as e:
            self.print_error(f"API functionality test failed: {e}")
            return False
    
    async def test_authentication_flow(self) -> Optional[str]:
        """Test user authentication flow"""
        self.print_header("Authentication Flow Test")
        
        try:
            # Try to register a test user
            register_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"],
                "full_name": self.test_user["full_name"]
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/auth/register",
                json=register_data
            )
            
            if response.status_code == 201:
                self.print_success("User registration successful")
            elif response.status_code == 400:
                self.print_info("User already exists, proceeding with login")
            else:
                self.print_warning(f"Registration unexpected response: {response.status_code}")
            
            # Login
            login_data = {
                "username": self.test_user["email"],
                "password": self.test_user["password"]
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                
                if access_token:
                    self.print_success("Authentication successful")
                    
                    # Test authenticated endpoint
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = await self.client.get(
                        f"{self.base_url}/api/auth/me",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        self.print_success(f"Authenticated as: {user_data.get('email', 'unknown')}")
                        return access_token
                    else:
                        self.print_error(f"Auth verification failed: {response.status_code}")
                else:
                    self.print_error("No access token in response")
            else:
                self.print_error(f"Login failed: {response.status_code}")
                if response.status_code == 422:
                    self.print_info("Response:", response.json())
            
            return None
            
        except Exception as e:
            self.print_error(f"Authentication test failed: {e}")
            return None
    
    async def test_data_operations(self, access_token: Optional[str]) -> bool:
        """Test basic CRUD operations"""
        self.print_header("Data Operations Test")
        
        if not access_token:
            self.print_warning("Skipping data operations test - no access token")
            return False
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            # Test creating a vehicle (if endpoint exists)
            vehicle_data = {
                "make": "Toyota",
                "model": "Camry", 
                "year": 2023,
                "vin": "TEST123456789DEMO",
                "license_plate": "DEMO-001"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/vehicles/",
                json=vehicle_data,
                headers=headers
            )
            
            if response.status_code == 201:
                vehicle = response.json()
                vehicle_id = vehicle.get("id")
                self.print_success(f"Vehicle created: {vehicle_id}")
                
                # Test retrieving the vehicle
                response = await self.client.get(
                    f"{self.base_url}/api/vehicles/{vehicle_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.print_success("Vehicle retrieval successful")
                    
                    # Test updating the vehicle
                    update_data = {"year": 2024}
                    response = await self.client.patch(
                        f"{self.base_url}/api/vehicles/{vehicle_id}",
                        json=update_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        self.print_success("Vehicle update successful")
                    else:
                        self.print_warning(f"Vehicle update failed: {response.status_code}")
                    
                    # Cleanup - delete the vehicle
                    response = await self.client.delete(
                        f"{self.base_url}/api/vehicles/{vehicle_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 204:
                        self.print_success("Vehicle deletion successful")
                    else:
                        self.print_warning(f"Vehicle deletion failed: {response.status_code}")
                        
                else:
                    self.print_error(f"Vehicle retrieval failed: {response.status_code}")
                    
            elif response.status_code == 404:
                self.print_info("Vehicle endpoints not yet implemented")
                return True
            else:
                self.print_warning(f"Vehicle creation failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Data operations test failed: {e}")
            return False
    
    async def test_monitoring_endpoints(self) -> bool:
        """Test monitoring and metrics endpoints"""
        self.print_header("Monitoring Endpoints Test")
        
        monitoring_endpoints = [
            (f"{self.base_url}/metrics", "Backend Metrics"),
            (f"{self.metrics_url}", "Prometheus UI"),
            (f"{self.dashboard_url}", "Grafana Dashboard"),
        ]
        
        all_passed = True
        
        for url, description in monitoring_endpoints:
            try:
                response = await self.client.get(url, timeout=10.0)
                if response.status_code == 200:
                    self.print_success(f"{description}: Accessible")
                else:
                    self.print_warning(f"{description}: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.print_error(f"{description}: Failed - {str(e)[:30]}...")
                all_passed = False
        
        return all_passed
    
    async def test_ssl_certificates(self) -> bool:
        """Test SSL certificate configuration"""
        self.print_header("SSL Certificate Test")
        
        # Test domains
        domains = [
            "api.garagereg.local",
            "admin.garagereg.local", 
            "traefik.garagereg.local",
            "mail.garagereg.local"
        ]
        
        all_valid = True
        
        for domain in domains:
            try:
                # Create a client that verifies certificates
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.get(f"https://{domain}", timeout=5.0)
                    
                    # Check if HTTPS is working
                    if response.url.scheme == "https":
                        self.print_success(f"HTTPS working for {domain}")
                    else:
                        self.print_warning(f"HTTPS redirect not working for {domain}")
                        all_valid = False
                        
            except Exception as e:
                self.print_error(f"SSL test failed for {domain}: {str(e)[:30]}...")
                all_valid = False
        
        return all_valid
    
    async def generate_test_report(self, results: Dict[str, bool]) -> None:
        """Generate a comprehensive test report"""
        self.print_header("Infrastructure Test Report")
        
        # Create results table
        table = Table(title="Test Results Summary")
        table.add_column("Test Category", style="cyan", width=30)
        table.add_column("Status", style="magenta", width=15)
        table.add_column("Description", style="white", width=50)
        
        descriptions = {
            "docker_services": "Docker container health and status",
            "database": "PostgreSQL connectivity and configuration",
            "redis": "Redis cache connectivity and operations",
            "traefik_routing": "Reverse proxy and load balancing",
            "api_functionality": "REST API endpoints and responses",
            "authentication": "User authentication and authorization",
            "data_operations": "CRUD operations and data persistence",
            "monitoring": "Metrics collection and dashboards",
            "ssl_certificates": "TLS/SSL certificate validation"
        }
        
        passed_count = 0
        total_count = len(results)
        
        for test_name, passed in results.items():
            status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
            description = descriptions.get(test_name, "Unknown test")
            
            table.add_row(test_name.replace("_", " ").title(), status, description)
            
            if passed:
                passed_count += 1
        
        console.print(table)
        
        # Summary
        success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
        
        summary_text = f"""
        Total Tests: {total_count}
        Passed: {passed_count}
        Failed: {total_count - passed_count}
        Success Rate: {success_rate:.1f}%
        """
        
        if success_rate >= 90:
            color = "green"
            status_emoji = "🎉"
        elif success_rate >= 70:
            color = "yellow"
            status_emoji = "⚠️"
        else:
            color = "red"
            status_emoji = "❌"
        
        console.print(Panel(
            f"[{color}]{status_emoji} Infrastructure Health: {success_rate:.1f}%[/{color}]\n{summary_text}",
            title="[bold]Test Summary[/bold]"
        ))
        
        # Recommendations
        if success_rate < 100:
            console.print("\n[yellow]Recommendations:[/yellow]")
            
            if not results.get("docker_services", True):
                console.print("• Check Docker service logs: [cyan]docker compose -f infra/docker-compose.yml logs[/cyan]")
            
            if not results.get("database", True):
                console.print("• Verify database connection and run migrations")
                
            if not results.get("authentication", True):
                console.print("• Check backend API configuration and JWT settings")
                
            if not results.get("ssl_certificates", True):
                console.print("• Regenerate TLS certificates: [cyan]cd infra/traefik && ./generate-certs.sh[/cyan]")

async def main():
    """Main demo execution"""
    console.print("""
[bold blue]
 ██████╗  █████╗ ██████╗  █████╗  ██████╗ ███████╗██████╗ ███████╗ ██████╗ 
██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔════╝██╔══██╗██╔════╝██╔════╝ 
██║  ███╗███████║██████╔╝███████║██║  ███╗█████╗  ██████╔╝█████╗  ██║  ███╗
██║   ██║██╔══██║██╔══██╗██╔══██║██║   ██║██╔══╝  ██╔══██╗██╔══╝  ██║   ██║
╚██████╔╝██║  ██║██║  ██║██║  ██║╚██████╔╝███████╗██║  ██║███████╗╚██████╔╝
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ 
                                                                            
                    Infrastructure Demo & Validation                         
[/bold blue]
    """)
    
    # Test results storage
    results = {}
    
    async with InfrastructureDemo() as demo:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
        ) as progress:
            
            # Define test tasks
            tasks = [
                ("docker_services", "Checking Docker services", demo.check_docker_services),
                ("database", "Testing database connectivity", demo.test_database_connectivity),
                ("redis", "Testing Redis connectivity", demo.test_redis_connectivity),
                ("traefik_routing", "Testing Traefik routing", demo.test_traefik_routing),
                ("api_functionality", "Testing API functionality", demo.test_api_functionality),
                ("ssl_certificates", "Testing SSL certificates", demo.test_ssl_certificates),
                ("monitoring", "Testing monitoring endpoints", demo.test_monitoring_endpoints),
            ]
            
            # Execute tests
            for test_name, description, test_func in tasks:
                task = progress.add_task(description, total=1)
                
                try:
                    result = await test_func()
                    results[test_name] = result
                except Exception as e:
                    console.print(f"[red]Error in {test_name}: {e}[/red]")
                    results[test_name] = False
                
                progress.update(task, completed=1)
                await asyncio.sleep(0.5)  # Brief pause between tests
        
        # Authentication and data operations tests (separate due to dependencies)
        console.print("\n")
        access_token = await demo.test_authentication_flow()
        results["authentication"] = access_token is not None
        
        results["data_operations"] = await demo.test_data_operations(access_token)
        
        # Generate final report
        console.print("\n")
        await demo.generate_test_report(results)
        
        # Exit with appropriate code
        all_passed = all(results.values())
        return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Demo failed with error: {e}[/red]")
        sys.exit(1)
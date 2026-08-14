#troubleshoot_config.py

"""
BatchETL Pipeline - Troubleshooting Configuration

Contains all configurable settings for troubleshooting scripts.
"""

from typing import Dict, List, Optional, Any

# ============================================
# Container Configuration
# ============================================

CONTAINERS: Dict[str, str] = {
    'postgres': 'batch-etl-postgres',
    'airflow': 'batch-etl-airflow',
    'streamlit': 'batch-etl-streamlit',
}

REQUIRED_CONTAINERS: List[str] = ['postgres', 'streamlit']
OPTIONAL_CONTAINERS: List[str] = ['airflow']

# ============================================
# Network Configuration
# ============================================

NETWORK_CONFIG: Dict[str, str] = {
    'name': 'batch-etl-network',
    'subnet': '172.28.0.0/16',
}

HOSTS: Dict[str, str] = {
    'postgres': '172.28.0.10',
    'airflow': '172.28.0.20',
    'streamlit': '172.28.0.30',
}

# ============================================
# Port Configuration
# ============================================

PORTS: Dict[str, int] = {
    'postgres': 5432,
    'airflow': 8080,
    'streamlit': 8501,
}

PORT_DESCRIPTIONS: Dict[int, str] = {
    5432: 'PostgreSQL',
    8080: 'Airflow UI',
    8501: 'Streamlit Dashboard',
}

# ============================================
# URL Configuration
# ============================================

URLS: Dict[str, str] = {
    'airflow_ui': 'http://localhost:8080',
    'streamlit_ui': 'http://localhost:8501',
    'api_dags': 'http://localhost:8080/api/v1/dags',
    'api_health': 'http://localhost:8080/health',
}

EXTERNAL_URLS: List[str] = [
    'https://github.com',
    'https://pypi.org',
    'https://hub.docker.com',
    'https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page',
]

# ============================================
# Database Configuration
# ============================================

DB_CONFIG: Dict[str, str] = {
    'user': 'admin',
    'password': 'admin',
    'database': 'warehouse',
    'host': 'postgres',
    'port': '5432',
}

# ============================================
# Airflow Configuration
# ============================================

AIRFLOW_CONFIG: Dict[str, str] = {
    'username': 'admin',
    'password': 'admin',
    'webserver': 'http://localhost:8080',
}

# ============================================
# Index Configuration
# ============================================

REQUIRED_INDEXES: List[str] = [
    'idx_pickup_datetime',
    'idx_pickup_day',
    'idx_fare_amount',
    'idx_trip_distance',
    'idx_vendor_id',
    'idx_pickup_hour',
    'idx_payment_type',
]

# ============================================
# DAG Configuration
# ============================================

DAG_CONFIG: Dict[str, str] = {
    'dag_id': 'etl_pipeline',
    'dag_file': 'dags/etl_pipeline.py',
    'schedule': '0 0 * * *',
}

DAG_TASKS: List[str] = [
    'extract_data',
    'transform_data',
    'load_data',
]

# ============================================
# Timeout Configuration
# ============================================

TIMEOUTS: Dict[str, int] = {
    'command': 30,
    'http': 10,
    'port_check': 2,
    'container_start': 60,
    'query': 30,
    'report': 300,
}

# ============================================
# File Paths
# ============================================

FILES: Dict[str, str] = {
    'compose': 'docker-compose.yml',
    'dag': 'dags/etl_pipeline.py',
    'readme': 'README.md',
    'license': 'LICENSE',
    'gitignore': '.gitignore',
    'env': '.env',
    'blueprint': 'docs/blueprint.md',
    'cheatsheet': 'docs/cheatsheets.md',
    'checklist': 'docs/verification-checklist.md',
}

DASHBOARD_FILES: List[str] = [
    'dashboard/app.py',
    'dashboard/Dockerfile',
    'dashboard/requirements.txt',
]

VERIFICATION_REPORTS: List[str] = [
    'phase1_verification.json',
    'phase2_verification.json',
    'phase3_verification.json',
    'phase4_verification.json',
    'phase5_verification.json',
    'phase6_verification.json',
    'phase7_verification.json',
    'phase8_verification.json',
    'phase9_verification.json',
]

# ============================================
# Required Dashboard Imports
# ============================================

REQUIRED_IMPORTS: List[str] = [
    'streamlit',
    'pandas',
    'plotly',
    'sqlalchemy',
    'create_engine',
]

DASHBOARD_KPIS: List[str] = [
    'Total Trips',
    'Average Fare',
    'Avg Distance',
    'Avg Passengers',
    'Total Revenue',
]

DASHBOARD_CHARTS: List[str] = [
    'Revenue by Day',
    'Trips per Hour',
    'Fare Distribution',
    'Distance vs Fare',
]

DASHBOARD_FILTERS: List[str] = [
    'Fare Range',
    'Distance Range',
    'Day of Week',
    'Payment Type',
    'Vendor ID',
]

# ============================================
# Data Quality Rules
# ============================================

DATA_QUALITY_RULES: Dict[str, Dict] = {
    'fare_amount': {
        'min': 0,
        'max': 500,
        'description': 'Fare amount between 0 and 500'
    },
    'trip_distance': {
        'min': 0,
        'max': 100,
        'description': 'Trip distance between 0 and 100 miles'
    },
    'passenger_count': {
        'min': 0,
        'max': None,
        'description': 'Passenger count >= 0'
    },
}

# ============================================
# Verification Scripts
# ============================================

VERIFICATION_SCRIPTS: List[str] = [
    'verify-phase-1.py',
    'verify-phase-2.py',
    'verify-phase-3.py',
    'verify-phase-4.py',
    'verify-phase-5.py',
    'verify-phase-6.py',
    'verify-phase-7.py',
    'verify-phase-8.py',
    'verify-phase-9.py',
]

TROUBLESHOOTING_SCRIPTS: List[str] = [
    'troubleshoot_docker.py',
    'troubleshoot_airflow.py',
    'troubleshoot_postgres.py',
    'troubleshoot_dashboard.py',
    'troubleshoot_network.py',
]

# ============================================
# Health Check Configuration
# ============================================

HEALTH_CHECK: Dict[str, Dict] = {
    'postgres': {
        'query': 'SELECT 1',
        'expected': '1',
        'timeout': 10,
    },
    'airflow': {
        'endpoint': '/health',
        'expected_status': 200,
        'timeout': 10,
    },
    'streamlit': {
        'endpoint': '/_stcore/health',
        'expected_status': 200,
        'timeout': 10,
    },
}

# ============================================
# Logging Configuration
# ============================================

LOG_CONFIG: Dict[str, str] = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'troubleshoot.log',
}

# ============================================
# Colors Configuration (for reference)
# ============================================

COLORS: Dict[str, str] = {
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'blue': '\033[94m',
    'cyan': '\033[96m',
    'magenta': '\033[95m',
    'bold': '\033[1m',
    'end': '\033[0m',
}

# ============================================
# Thresholds
# ============================================

THRESHOLDS: Dict[str, Dict] = {
    'data_count': {
        'min_required': 100000,
        'warning': 50000,
    },
    'load_time': {
        'max_seconds': 30,
        'warning_seconds': 15,
    },
    'file_size': {
        'max_mb': 500,
        'warning_mb': 300,
    },
    'memory_usage': {
        'max_mb': 2048,
        'warning_mb': 1024,
    },
    'disk_space': {
        'min_gb': 10,
        'warning_gb': 20,
    },
    'response_time': {
        'max_ms': 500,
        'warning_ms': 200,
    },
}

# ============================================
# Validation Rules
# ============================================

VALIDATION_RULES: Dict[str, Dict] = {
    'trip_id': {
        'type': 'integer',
        'nullable': False,
        'unique': True,
    },
    'vendor_id': {
        'type': 'integer',
        'nullable': False,
        'allowed_values': [1, 2],
    },
    'payment_type': {
        'type': 'integer',
        'nullable': False,
        'allowed_values': [1, 2, 3, 4, 5, 6],
    },
}

# ============================================
# Test Data
# ============================================

TEST_QUERIES: Dict[str, str] = {
    'count_all': 'SELECT COUNT(*) FROM fact_trips;',
    'sample': 'SELECT * FROM fact_trips LIMIT 10;',
    'duplicates': 'SELECT trip_id, COUNT(*) FROM fact_trips GROUP BY trip_id HAVING COUNT(*) > 1;',
    'null_check': 'SELECT COUNT(*) FROM fact_trips WHERE pickup_datetime IS NULL;',
}

# ============================================
# Report Configuration
# ============================================

REPORT_CONFIG: Dict[str, str] = {
    'json_file': 'all_checks_report.json',
    'text_file': 'all_checks_report.txt',
    'html_file': 'all_checks_report.html',
}
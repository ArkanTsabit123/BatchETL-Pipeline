# data_inspection.py
"""
Detailed Data Inspection Script for BatchETL Pipeline.

This script provides comprehensive data inspection for the NYC Taxi dataset.
It checks data quality, statistics, distributions, and potential issues.

Usage:
    python data_inspection.py --all           # Run all inspections
    python data_inspection.py --schema        # Check schema only
    python data_inspection.py --stats         # Generate statistics
    python data_inspection.py --quality       # Check data quality
    python data_inspection.py --sample        # View sample data
    python data_inspection.py --outliers      # Detect outliers
    python data_inspection.py --correlation   # Correlation analysis
    python data_inspection.py --report        # Generate full report
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
import json
from typing import Dict, Any, List, Optional, Tuple


class Colors:
    """Terminal color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DataInspector:
    """
    Data inspector for NYC Taxi dataset.
    """

    def __init__(self, file_path: str = "data/staging/taxi_clean.csv"):
        """
        Initialize the data inspector.

        Args:
            file_path: Path to the CSV file.
        """
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.stats: Dict[str, Any] = {}
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def load_data(self) -> bool:
        """
        Load the dataset into DataFrame.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.file_path.exists():
            print(f"{Colors.RED}File not found: {self.file_path}{Colors.END}")
            return False

        try:
            print(f"{Colors.CYAN}Loading data from: {self.file_path}{Colors.END}")
            self.df = pd.read_csv(self.file_path, low_memory=False)
            print(f"{Colors.GREEN}Loaded {len(self.df):,} rows and {len(self.df.columns)} columns{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}Error loading data: {str(e)}{Colors.END}")
            return False

    def print_section(self, title: str, char: str = "=") -> None:
        """Print a formatted section header."""
        print(f"\n{Colors.CYAN}{char * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
        print(f"{Colors.CYAN}{char * 60}{Colors.END}\n")

    def print_check(self, text: str, status: bool, detail: str = "") -> None:
        """Print a check result."""
        icon = "✓" if status else "✗"
        color = Colors.GREEN if status else Colors.RED
        if detail:
            print(f"  {color}{icon} {text}{Colors.END}")
            print(f"     {Colors.CYAN}-> {detail}{Colors.END}")
        else:
            print(f"  {color}{icon} {text}{Colors.END}")

    def print_value(self, label: str, value: Any, color: str = Colors.GREEN) -> None:
        """Print a key-value pair."""
        print(f"  {Colors.BOLD}{label}:{Colors.END} {color}{value}{Colors.END}")

    def inspect_schema(self) -> Dict[str, Any]:
        """
        Inspect dataset schema.

        Returns:
            Dict containing schema information.
        """
        self.print_section("DATASET SCHEMA")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return {}

        schema_info = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "memory_usage": f"{self.df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB",
            "columns": {}
        }

        print(f"{Colors.BOLD}General Information:{Colors.END}")
        self.print_value("Total Rows", f"{len(self.df):,}")
        self.print_value("Total Columns", len(self.df.columns))
        self.print_value("Memory Usage", schema_info["memory_usage"])
        print()

        print(f"{Colors.BOLD}Column Details:{Colors.END}")
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            null_count = self.df[col].isnull().sum()
            null_pct = (null_count / len(self.df)) * 100
            unique_count = self.df[col].nunique()

            schema_info["columns"][col] = {
                "dtype": dtype,
                "null_count": int(null_count),
                "null_percentage": round(null_pct, 2),
                "unique_count": int(unique_count),
            }

            status = null_count == 0
            detail = f"dtype: {dtype}, nulls: {null_count:,} ({null_pct:.1f}%), unique: {unique_count:,}"
            self.print_check(f"{col}", status, detail)

        self.stats["schema"] = schema_info
        return schema_info

    def inspect_statistics(self) -> Dict[str, Any]:
        """
        Generate statistical summary.

        Returns:
            Dict containing statistical information.
        """
        self.print_section("STATISTICAL SUMMARY")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return {}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()

        print(f"{Colors.BOLD}Numeric Columns: {', '.join(numeric_cols)}{Colors.END}")
        print(f"{Colors.BOLD}Categorical Columns: {', '.join(categorical_cols)}{Colors.END}\n")

        stats_info = {
            "numeric_columns": {},
            "categorical_columns": {}
        }

        if numeric_cols:
            print(f"{Colors.BOLD}Numeric Column Statistics:{Colors.END}")
            for col in numeric_cols:
                desc = self.df[col].describe()
                stats_info["numeric_columns"][col] = {
                    "count": int(desc['count']),
                    "mean": float(desc['mean']),
                    "std": float(desc['std']),
                    "min": float(desc['min']),
                    "25%": float(desc['25%']),
                    "50%": float(desc['50%']),
                    "75%": float(desc['75%']),
                    "max": float(desc['max'])
                }
                print(f"\n  {Colors.BOLD}{col}:{Colors.END}")
                print(f"    count: {desc['count']:,.0f}")
                print(f"    mean:  {desc['mean']:.4f}")
                print(f"    std:   {desc['std']:.4f}")
                print(f"    min:   {desc['min']:.4f}")
                print(f"    25%:   {desc['25%']:.4f}")
                print(f"    50%:   {desc['50%']:.4f}")
                print(f"    75%:   {desc['75%']:.4f}")
                print(f"    max:   {desc['max']:.4f}")

        if categorical_cols:
            print(f"\n{Colors.BOLD}Categorical Column Statistics:{Colors.END}")
            for col in categorical_cols:
                value_counts = self.df[col].value_counts()
                top_values = value_counts.head(5).to_dict()
                stats_info["categorical_columns"][col] = {
                    "unique_count": len(value_counts),
                    "top_values": top_values
                }
                print(f"\n  {Colors.BOLD}{col}:{Colors.END}")
                print(f"    unique: {len(value_counts):,}")
                print(f"    top values: {dict(list(top_values.items())[:5])}")

        self.stats["statistics"] = stats_info
        return stats_info

    def inspect_quality(self) -> Dict[str, Any]:
        """
        Check data quality.

        Returns:
            Dict containing quality issues.
        """
        self.print_section("DATA QUALITY")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return {}

        quality_info = {
            "nulls": {},
            "duplicates": 0,
            "outliers": {},
            "issues": []
        }

        print(f"{Colors.BOLD}Null Value Analysis:{Colors.END}")
        for col in self.df.columns:
            null_count = self.df[col].isnull().sum()
            null_pct = (null_count / len(self.df)) * 100
            quality_info["nulls"][col] = {
                "count": int(null_count),
                "percentage": round(null_pct, 2)
            }
            status = null_count == 0
            detail = f"{null_count:,} ({null_pct:.1f}%)" if null_count > 0 else "No nulls"
            self.print_check(f"{col}", status, detail)

        print(f"\n{Colors.BOLD}Duplicate Analysis:{Colors.END}")
        duplicates = self.df.duplicated().sum()
        quality_info["duplicates"] = int(duplicates)
        status = duplicates == 0
        self.print_check(f"Duplicate rows", status, f"{duplicates:,} duplicates found")

        print(f"\n{Colors.BOLD}Outlier Detection (IQR Method):{Colors.END}")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            if col in ['trip_id', 'pickup_hour', 'pickup_month']:
                continue
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            outlier_count = len(outliers)
            outlier_pct = (outlier_count / len(self.df)) * 100
            quality_info["outliers"][col] = {
                "count": outlier_count,
                "percentage": round(outlier_pct, 2),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound)
            }
            # Skip vendor_id because it's categorical
            if col == 'vendor_id':
                status = True
                detail = "Categorical column - outliers not applicable"
            else:
                status = outlier_count < len(self.df) * 0.05
                detail = f"{outlier_count:,} ({outlier_pct:.1f}%) outliers"
            self.print_check(f"{col}", status, detail)

        self.stats["quality"] = quality_info
        return quality_info

    def inspect_sample(self, n: int = 10) -> pd.DataFrame:
        """
        View sample data.

        Args:
            n: Number of rows to display.

        Returns:
            DataFrame with sample data.
        """
        self.print_section(f"SAMPLE DATA (First {n} rows)")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return pd.DataFrame()

        sample = self.df.head(n)

        with pd.option_context('display.max_columns', None, 'display.width', None):
            print(sample.to_string(index=False))

        return sample

    def inspect_correlation(self) -> Dict[str, Any]:
        """
        Analyze correlations between numeric columns.

        Returns:
            Dict containing correlation matrix.
        """
        self.print_section("CORRELATION ANALYSIS")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return {}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if 'trip_id' in numeric_cols:
            numeric_cols.remove('trip_id')

        if len(numeric_cols) < 2:
            print(f"{Colors.YELLOW}Not enough numeric columns for correlation analysis.{Colors.END}")
            return {}

        correlation_matrix = self.df[numeric_cols].corr()
        correlation_info = {
            "matrix": correlation_matrix.to_dict(),
            "high_correlations": []
        }

        print(f"{Colors.BOLD}Correlation Matrix:{Colors.END}")
        print(correlation_matrix.round(4).to_string())

        print(f"\n{Colors.BOLD}High Correlations (|r| > 0.7):{Colors.END}")
        for i in range(len(correlation_matrix.columns)):
            for j in range(i + 1, len(correlation_matrix.columns)):
                col1 = correlation_matrix.columns[i]
                col2 = correlation_matrix.columns[j]
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) > 0.7:
                    correlation_info["high_correlations"].append({
                        "col1": col1,
                        "col2": col2,
                        "correlation": float(corr)
                    })
                    print(f"  {col1} ↔ {col2}: {corr:.4f}")

        self.stats["correlation"] = correlation_info
        return correlation_info

    def inspect_outliers(self) -> Dict[str, Any]:
        """
        Detailed outlier detection.

        Returns:
            Dict containing detailed outlier information.
        """
        self.print_section("DETAILED OUTLIER ANALYSIS")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return {}

        outlier_info = {}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if 'trip_id' in numeric_cols:
            numeric_cols.remove('trip_id')

        for col in numeric_cols:
            print(f"\n{Colors.BOLD}{col}:{Colors.END}")

            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            outlier_count = len(outliers)

            print(f"  Q1: {Q1:.4f}")
            print(f"  Q3: {Q3:.4f}")
            print(f"  IQR: {IQR:.4f}")
            print(f"  Lower Bound: {lower_bound:.4f}")
            print(f"  Upper Bound: {upper_bound:.4f}")
            print(f"  Outliers: {outlier_count:,} ({outlier_count/len(self.df)*100:.1f}%)")

            outlier_info[col] = {
                "Q1": float(Q1),
                "Q3": float(Q3),
                "IQR": float(IQR),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_count": int(outlier_count),
                "outlier_percentage": round(outlier_count / len(self.df) * 100, 2)
            }

        self.stats["outliers"] = outlier_info
        return outlier_info

    def inspect_distribution(self) -> Dict[str, Any]:
        """
        Analyze column distributions.

        Returns:
            Dict containing distribution information.
        """
        self.print_section("DISTRIBUTION ANALYSIS")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return {}

        dist_info = {}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols:
            if col == 'trip_id' or col == 'pickup_month':
                continue
            print(f"\n{Colors.BOLD}{col}:{Colors.END}")

            data = self.df[col].dropna()
            skewness = data.skew()
            kurtosis = data.kurtosis()

            print(f"  Skewness: {skewness:.4f}")
            print(f"  Kurtosis: {kurtosis:.4f}")

            if skewness > 1:
                print(f"  {Colors.YELLOW}→ Highly positive skew (right-tailed){Colors.END}")
            elif skewness < -1:
                print(f"  {Colors.YELLOW}→ Highly negative skew (left-tailed){Colors.END}")
            elif skewness > 0.5:
                print(f"  {Colors.CYAN}→ Moderately positive skew{Colors.END}")
            elif skewness < -0.5:
                print(f"  {Colors.CYAN}→ Moderately negative skew{Colors.END}")
            else:
                print(f"  {Colors.GREEN}→ Approximately symmetric{Colors.END}")

            dist_info[col] = {
                "skewness": float(skewness),
                "kurtosis": float(kurtosis)
            }

        self.stats["distribution"] = dist_info
        return dist_info

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.

        Returns:
            Dict containing full report.
        """
        self.print_section("DATA INSPECTION REPORT")

        if self.df is None:
            print(f"{Colors.RED}No data loaded. Please load data first.{Colors.END}")
            return {}

        print(f"{Colors.BOLD}Generating comprehensive report...{Colors.END}\n")

        self.inspect_schema()
        self.inspect_statistics()
        self.inspect_quality()
        self.inspect_correlation()
        self.inspect_distribution()

        report = self.stats.copy()
        report["timestamp"] = datetime.now().isoformat()
        report["file_path"] = str(self.file_path)

        report_path = Path("data_inspection_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n{Colors.GREEN}Report saved to: {report_path}{Colors.END}")

        return report

    def run_all(self) -> None:
        """Run all inspection methods."""
        if not self.load_data():
            return

        self.generate_report()

        summary = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    DATA INSPECTION SUMMARY                       ║
╠═══════════════════════════════════════════════════════════════════╣
║  File:           {str(self.file_path):<44} ║
║  Total Rows:     {len(self.df):>15,} rows                          ║
║  Total Columns:  {len(self.df.columns):>15} columns                          ║
║  Memory Usage:   {self.df.memory_usage(deep=True).sum() / (1024 ** 2):>15.2f} MB                          ║
║  Duplicates:     {self.df.duplicated().sum():>15,} rows                          ║
║  Null Cells:     {self.df.isnull().sum().sum():>15,} cells                          ║
╚═══════════════════════════════════════════════════════════════════╝
        """
        print(f"\n{Colors.CYAN}{summary}{Colors.END}")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Detailed Data Inspection for BatchETL Pipeline")
    parser.add_argument("--file", type=str, default="data/staging/taxi_clean.csv",
                        help="Path to the CSV file")
    parser.add_argument("--all", action="store_true", help="Run all inspections")
    parser.add_argument("--schema", action="store_true", help="Check schema only")
    parser.add_argument("--stats", action="store_true", help="Generate statistics")
    parser.add_argument("--quality", action="store_true", help="Check data quality")
    parser.add_argument("--sample", action="store_true", help="View sample data")
    parser.add_argument("--outliers", action="store_true", help="Detect outliers")
    parser.add_argument("--correlation", action="store_true", help="Correlation analysis")
    parser.add_argument("--distribution", action="store_true", help="Distribution analysis")
    parser.add_argument("--report", action="store_true", help="Generate full report")

    args = parser.parse_args()

    inspector = DataInspector(args.file)

    if not inspector.load_data():
        sys.exit(1)

    if args.schema:
        inspector.inspect_schema()
    elif args.stats:
        inspector.inspect_statistics()
    elif args.quality:
        inspector.inspect_quality()
    elif args.sample:
        inspector.inspect_sample()
    elif args.outliers:
        inspector.inspect_outliers()
    elif args.correlation:
        inspector.inspect_correlation()
    elif args.distribution:
        inspector.inspect_distribution()
    elif args.report:
        inspector.generate_report()
    else:
        inspector.run_all()


if __name__ == "__main__":
    main()
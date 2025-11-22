"""
Lambda function for data quality checks.
Validates row counts, null percentages, duplicates, and data freshness.
"""

import json
import boto3
from datetime import datetime, timedelta
import logging
from typing import Dict, List

logger = logging.getLogger()
logger.setLevel(logging.INFO)

athena_client = boto3.client("athena")
s3_client = boto3.client("s3")
sns_client = boto3.client("sns")


class DataQualityChecker:
    """Perform data quality checks on processed data."""

    def __init__(
        self, database: str, workgroup: str = "primary", output_location: str = None
    ):
        self.database = database
        self.workgroup = workgroup
        self.output_location = output_location
        self.checks_passed = []
        self.checks_failed = []

    def execute_query(self, query: str) -> List[Dict]:
        """Execute Athena query and return results."""
        try:
            response = athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={"Database": self.database},
                WorkGroup=self.workgroup,
                ResultConfiguration={"OutputLocation": self.output_location},
            )

            query_execution_id = response["QueryExecutionId"]

            # Wait for query to complete
            while True:
                response = athena_client.get_query_execution(
                    QueryExecutionId=query_execution_id
                )
                state = response["QueryExecution"]["Status"]["State"]

                if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                    break

                import time

                time.sleep(1)

            if state != "SUCCEEDED":
                raise Exception(f"Query failed with state: {state}")

            # Get results
            response = athena_client.get_query_results(
                QueryExecutionId=query_execution_id
            )

            rows = response["ResultSet"]["Rows"]
            if len(rows) <= 1:
                return []

            # Parse results
            headers = [col["VarCharValue"] for col in rows[0]["Data"]]
            results = []
            for row in rows[1:]:
                values = [col.get("VarCharValue") for col in row["Data"]]
                results.append(dict(zip(headers, values)))

            return results

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def check_row_count(self, table_name: str, expected_min: int) -> bool:
        """Check if table has minimum number of rows."""
        check_name = f"Row count check for {table_name}"

        try:
            query = f"SELECT COUNT(*) as cnt FROM {table_name}"
            results = self.execute_query(query)

            if not results:
                self.checks_failed.append(
                    {"check": check_name, "reason": "No results returned"}
                )
                return False

            count = int(results[0]["cnt"])

            if count < expected_min:
                self.checks_failed.append(
                    {
                        "check": check_name,
                        "reason": f"Row count {count} below threshold {expected_min}",
                    }
                )
                return False

            self.checks_passed.append({"check": check_name, "value": count})
            return True

        except Exception as e:
            self.checks_failed.append({"check": check_name, "reason": str(e)})
            return False

    def check_null_percentages(
        self, table_name: str, columns: List[str], max_null_pct: float = 0.1
    ) -> bool:
        """Check null percentages for critical columns."""
        check_name = f"Null percentage check for {table_name}"
        all_passed = True

        try:
            for column in columns:
                query = f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) as nulls
                    FROM {table_name}
                """
                results = self.execute_query(query)

                if not results:
                    continue

                total = int(results[0]["total"])
                nulls = int(results[0]["nulls"])
                null_pct = nulls / total if total > 0 else 0

                if null_pct > max_null_pct:
                    self.checks_failed.append(
                        {
                            "check": f"{check_name} - {column}",
                            "reason": f"Null percentage {null_pct:.2%} exceeds threshold {max_null_pct:.2%}",
                        }
                    )
                    all_passed = False
                else:
                    self.checks_passed.append(
                        {
                            "check": f"{check_name} - {column}",
                            "value": f"{null_pct:.2%}",
                        }
                    )

            return all_passed

        except Exception as e:
            self.checks_failed.append({"check": check_name, "reason": str(e)})
            return False

    def check_duplicates(self, table_name: str, unique_columns: List[str]) -> bool:
        """Check for duplicate records."""
        check_name = f"Duplicate check for {table_name}"

        try:
            cols = ", ".join(unique_columns)
            query = f"""
                SELECT COUNT(*) as duplicate_count
                FROM (
                    SELECT {cols}, COUNT(*) as cnt
                    FROM {table_name}
                    GROUP BY {cols}
                    HAVING COUNT(*) > 1
                )
            """
            results = self.execute_query(query)

            if not results:
                self.checks_passed.append({"check": check_name, "value": 0})
                return True

            duplicate_count = int(results[0]["duplicate_count"])

            if duplicate_count > 0:
                self.checks_failed.append(
                    {
                        "check": check_name,
                        "reason": f"Found {duplicate_count} duplicate records",
                    }
                )
                return False

            self.checks_passed.append({"check": check_name, "value": 0})
            return True

        except Exception as e:
            self.checks_failed.append({"check": check_name, "reason": str(e)})
            return False

    def check_data_freshness(
        self, table_name: str, date_column: str, max_age_hours: int = 24
    ) -> bool:
        """Check if data is recent."""
        check_name = f"Data freshness check for {table_name}"

        try:
            query = f"""
                SELECT MAX({date_column}) as latest_date
                FROM {table_name}
            """
            results = self.execute_query(query)

            if not results or not results[0]["latest_date"]:
                self.checks_failed.append(
                    {"check": check_name, "reason": "No date found"}
                )
                return False

            latest_date_str = results[0]["latest_date"]
            latest_date = datetime.fromisoformat(latest_date_str.replace("Z", "+00:00"))
            age_hours = (
                datetime.now() - latest_date.replace(tzinfo=None)
            ).total_seconds() / 3600

            if age_hours > max_age_hours:
                self.checks_failed.append(
                    {
                        "check": check_name,
                        "reason": f"Data is {age_hours:.1f} hours old (threshold: {max_age_hours})",
                    }
                )
                return False

            self.checks_passed.append(
                {"check": check_name, "value": f"{age_hours:.1f} hours old"}
            )
            return True

        except Exception as e:
            self.checks_failed.append({"check": check_name, "reason": str(e)})
            return False

    def get_summary(self) -> Dict:
        """Get summary of all checks."""
        total_checks = len(self.checks_passed) + len(self.checks_failed)

        return {
            "total_checks": total_checks,
            "passed": len(self.checks_passed),
            "failed": len(self.checks_failed),
            "success_rate": (
                len(self.checks_passed) / total_checks if total_checks > 0 else 0
            ),
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "all_passed": len(self.checks_failed) == 0,
        }


def lambda_handler(event, context):
    """
    Lambda handler for data quality checks.

    Event format:
    {
        "database": "analytics_dev",
        "output_location": "s3://bucket/athena-results/",
        "sns_topic_arn": "arn:aws:sns:...:data-quality-alerts"
    }
    """
    try:
        database = event.get("database", "analytics_dev")
        output_location = event.get("output_location")
        sns_topic_arn = event.get("sns_topic_arn")

        logger.info(f"Running data quality checks for database: {database}")

        checker = DataQualityChecker(database, output_location=output_location)

        # Run checks for transactions table
        checker.check_row_count("transactions", expected_min=100)
        checker.check_null_percentages(
            "transactions",
            ["transaction_id", "customer_id", "product_id", "total_amount"],
            max_null_pct=0.01,
        )
        checker.check_duplicates("transactions", ["transaction_id"])
        checker.check_data_freshness(
            "transactions", "transaction_date", max_age_hours=48
        )

        # Run checks for products table
        checker.check_row_count("products", expected_min=10)
        checker.check_null_percentages(
            "products", ["product_id", "name", "category", "price"], max_null_pct=0.01
        )
        checker.check_duplicates("products", ["product_id"])

        # Get summary
        summary = checker.get_summary()

        logger.info(f"Data quality check summary: {json.dumps(summary)}")

        # Send SNS notification if checks failed
        if not summary["all_passed"] and sns_topic_arn:
            message = f"""
Data Quality Check Alert

Total Checks: {summary['total_checks']}
Passed: {summary['passed']}
Failed: {summary['failed']}
Success Rate: {summary['success_rate']:.1%}

Failed Checks:
{json.dumps(summary['checks_failed'], indent=2)}
"""
            sns_client.publish(
                TopicArn=sns_topic_arn,
                Subject="Data Quality Check Failed",
                Message=message,
            )

        return {
            "statusCode": 200 if summary["all_passed"] else 400,
            "body": json.dumps(summary),
            "quality_check_result": summary,
        }

    except Exception as e:
        logger.error(f"Error in data quality check: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

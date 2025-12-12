#!/usr/bin/env python
"""Example script demonstrating how to fetch data from Statistics Canada WDS.

IMPORTANT: This script is for demonstration purposes only. The main site does NOT
depend on this script - all examples use committed data snapshots in docs/assets/data/.

This shows how you COULD fetch real data from StatCan's Web Data Service (WDS)
if you wanted to update the examples or explore other indicators.

Usage:
    python scripts/fetch_statcan_example.py

Requirements:
    pip install requests pandas
"""

import json
from pathlib import Path

# These are just example table IDs - actual usage would require knowing
# the specific table and vectors you need
EXAMPLE_TABLE = "13-10-0394-01"  # Leading causes of death


def fetch_statcan_table_info(table_id: str) -> dict:
    """Fetch metadata about a Statistics Canada table.

    This demonstrates the API structure but doesn't actually fetch data
    to avoid network dependencies in the example.
    """
    # StatCan WDS endpoint
    base_url = "https://www150.statcan.gc.ca/t1/wds/rest"

    # Example endpoints (not called by default):
    # - Get cube metadata: {base_url}/getCubeMetadata
    # - Get data: {base_url}/getDataFromCubePidCoordAndLatestNPeriods

    return {
        "note": "This is a demonstration script",
        "table_id": table_id,
        "api_docs": "https://www.statcan.gc.ca/eng/developers/wds",
        "example_endpoint": f"{base_url}/getCubeMetadata",
        "request_body_example": json.dumps([{"productId": table_id}]),
    }


def main():
    """Show example of how to work with StatCan data."""
    print("Statistics Canada Web Data Service Example")
    print("=" * 50)
    print()
    print("NOTE: This script demonstrates the API structure but does NOT")
    print("make actual network calls. The indicator-recipes site uses")
    print("committed data snapshots only.")
    print()

    info = fetch_statcan_table_info(EXAMPLE_TABLE)

    print(f"Example table: {info['table_id']}")
    print(f"API documentation: {info['api_docs']}")
    print()
    print("To fetch real data, you would:")
    print("1. Find your table ID on statcan.gc.ca")
    print("2. Use the WDS REST API to fetch data")
    print("3. Process the JSON response into a DataFrame")
    print()
    print("Example API call structure:")
    print(f"  POST {info['example_endpoint']}")
    print(f"  Body: {info['request_body_example']}")
    print()
    print("For this project, we've committed small CSV snapshots to avoid")
    print("network dependencies and ensure reproducibility.")


if __name__ == "__main__":
    main()

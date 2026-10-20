"""
Single-file Chartink dashboard to Google Sheets uploader.

Required environment variables:
    GOOGLE_SHEET_ID       Target Google spreadsheet ID.
    GOOGLE_CREDENTIALS    Path to a Google service-account JSON file.

Optional environment variables:
    GOOGLE_CREDENTIALS_JSON  Full service-account JSON text instead of a file path.
    CHARTINK_DASHBOARD_URL   Chartink dashboard URL.
    CHARTINK_EMAIL           Chartink login email for private dashboards.
    CHARTINK_PASSWORD        Chartink login password for private dashboards.

Run:
    python chartink_GoogleExcel.py
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import webbrowser
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pytz
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build


DASHBOARD_URL = os.getenv("CHARTINK_DASHBOARD_URL", "https://chartink.com/dashboard/45863")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1xffV0Wf04TkM2opaVbd0yoiI3Xzj92veEGyAXjz9bSk")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", r"C:\Users\nelvi\Documents\pyprojects\pycodes\chartink\key\zippy-parity-491303-v5-dec4f4fe1ab6.json")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
CHARTINK_EMAIL = os.getenv("CHARTINK_EMAIL", "")
CHARTINK_PASSWORD = os.getenv("CHARTINK_PASSWORD", "")
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

ALL_DATA_SHEET = "All_Data"
SUMMARY_SHEET = "Daily_Summary"
TEMPLATE_SHEET = "Backtest_Template"
ALL_DATA_HEADERS = ["Date", "Scanner", "Symbol", "Company", "Price", "Market Cap", "% Change"]
SUMMARY_HEADERS = ["Date", "Scanner", "Stock Count", "Symbols"]
TEMPLATE_HEADER_ROWS = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("chartink_google_excel")

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://chartink.com/",
})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Chartink dashboard rows and append them to Google Sheets.")
    parser.add_argument("--date", help="Override run date written to the sheet, for example 28-Apr-2026.")
    parser.add_argument("--dashboard-url", default=DASHBOARD_URL, help="Chartink dashboard URL.")
    parser.add_argument("--spreadsheet-id", default=GOOGLE_SHEET_ID, help="Google spreadsheet ID.")
    parser.add_argument("--credentials", default=GOOGLE_CREDENTIALS, help="Path to service-account JSON.")
    parser.add_argument(
        "--cleanup-tabs",
        action="store_true",
        help="Delete old scanner/year tabs and keep only All_Data, Daily_Summary, and Backtest_Template.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the Google Sheet in the browser after upload.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch Chartink data and print the planned sheet output without uploading.",
    )
    parser.add_argument(
        "--no-template",
        action="store_true",
        help="Do not rebuild the Backtest_Template tab after upload.",
    )
    parser.add_argument(
        "--template-only",
        action="store_true",
        help="Only rebuild Backtest_Template from All_Data; do not fetch Chartink.",
    )
    return parser.parse_args()


def chartink_login() -> bool:
    """Log in to Chartink when credentials are configured."""
    if not CHARTINK_EMAIL or not CHARTINK_PASSWORD:
        log.info("Chartink credentials not set; fetching dashboard as guest.")
        return False

    try:
        response = session.get("https://chartink.com/login", timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        csrf = soup.find("meta", {"name": "csrf-token"})
        if not csrf:
            log.error("Chartink login page did not include a CSRF token.")
            return False

        response = session.post(
            "https://chartink.com/login",
            data={
                "_token": csrf["content"],
                "email": CHARTINK_EMAIL,
                "password": CHARTINK_PASSWORD,
            },
            timeout=15,
            allow_redirects=True,
        )
        if "logout" in response.text.lower() or response.url == "https://chartink.com/":
            log.info("Chartink login successful.")
            return True

        log.error("Chartink login failed. Check CHARTINK_EMAIL and CHARTINK_PASSWORD.")
        return False
    except Exception as exc:
        log.error(f"Chartink login error: {exc}")
        return False


def split_chartink_query(query: str) -> tuple[str, str]:
    """Split a dashboard widget query into Chartink column and scan clauses."""
    upper = query.upper()
    where_idx = upper.find(" WHERE(")
    if where_idx == -1:
        where_idx = upper.find(" WHERE ")
    if where_idx == -1:
        return "", query

    group_idx = upper.rfind(" GROUP BY ")
    column_clause = query[:where_idx].replace("select ", "", 1).strip()
    scan_clause = query[where_idx:group_idx].strip() if group_idx > 0 else query[where_idx:].strip()
    scan_clause = re.sub(r"^WHERE\s*", "", scan_clause, flags=re.IGNORECASE).strip()
    return column_clause, scan_clause


def fetch_chartink_dashboard(dashboard_url: str) -> list[dict]:
    """Fetch all scanner rows from a Chartink dashboard."""
    try:
        response = session.get(dashboard_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        log.error(f"Could not fetch Chartink dashboard: {exc}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    csrf_tag = soup.find("meta", {"name": "csrf-token"})
    if not csrf_tag:
        log.error("Chartink dashboard did not include a CSRF token.")
        return []

    widgets_match = re.search(r':widgets="(\[.*?\])"', response.text, re.DOTALL)
    if not widgets_match:
        log.error("Could not find Chartink dashboard widgets in page HTML.")
        return []

    widgets = json.loads(html.unescape(widgets_match.group(1)))
    api_headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRF-TOKEN": csrf_tag["content"],
        "Referer": dashboard_url,
    }

    rows: list[dict] = []
    for widget in widgets:
        query = widget.get("query", "")
        scanner_name = widget.get("name", "Scanner")
        if not query:
            continue

        column_clause, scan_clause = split_chartink_query(query)
        try:
            scan_response = session.post(
                "https://chartink.com/screener/process",
                data={"scan_clause": scan_clause, "column_clause": column_clause},
                headers={**session.headers, **api_headers},
                timeout=20,
            )
            scan_data = scan_response.json()
        except Exception as exc:
            log.error(f"Scan failed for '{scanner_name}': {exc}")
            continue

        if scan_data.get("scan_error"):
            log.warning(f"{scanner_name}: {scan_data['scan_error']}")
            continue

        for stock in scan_data.get("data", []):
            rows.append({
                "scanner": scanner_name,
                "symbol": stock.get("nsecode", ""),
                "name": stock.get("name", ""),
                "price": stock.get("price", ""),
                "mcap": stock.get("mcap", ""),
                "pct": stock.get("%", ""),
            })

    log.info(f"Fetched {len(rows)} rows from {len(widgets)} Chartink scanner widgets.")
    return rows


def get_sheets_service(credentials_path: str):
    """Build the Google Sheets API client."""
    if GOOGLE_CREDENTIALS_JSON:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(GOOGLE_CREDENTIALS_JSON),
            scopes=GOOGLE_SCOPES,
        )
    else:
        if not credentials_path:
            raise ValueError("Set GOOGLE_CREDENTIALS or pass --credentials with a service-account JSON path.")
        resolved_path = Path(credentials_path).expanduser().resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"Google credentials file not found: {resolved_path}")
        credentials = service_account.Credentials.from_service_account_file(
            str(resolved_path),
            scopes=GOOGLE_SCOPES,
        )
    return build("sheets", "v4", credentials=credentials)


def sanitize_sheet_title(name: str) -> str:
    """Make a string safe for use as a Google Sheets tab title."""
    cleaned = re.sub(r"[\[\]\*\?/\\:]", "_", str(name)).strip()
    return cleaned[:100] or "Scanner"


def get_sheet_map(service, spreadsheet_id: str) -> dict[str, int]:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {
        sheet["properties"]["title"]: sheet["properties"]["sheetId"]
        for sheet in metadata.get("sheets", [])
    }


def ensure_sheet(
    service,
    spreadsheet_id: str,
    sheet_name: str,
    sheet_map: dict[str, int],
    column_count: int,
) -> tuple[int, bool]:
    """Return sheet ID and whether the sheet was newly created."""
    if sheet_name in sheet_map:
        return sheet_map[sheet_name], False

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [{
                "addSheet": {
                    "properties": {
                        "title": sheet_name,
                        "gridProperties": {"rowCount": 2000, "columnCount": column_count},
                    }
                }
            }]
        },
    ).execute()
    sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]
    sheet_map[sheet_name] = sheet_id
    log.info(f"Created worksheet: {sheet_name}")
    return sheet_id, True


def get_existing_keys(
    service,
    spreadsheet_id: str,
    sheet_name: str,
    read_range: str,
    key_columns: tuple[int, ...],
) -> set[tuple[str, ...]]:
    """Read existing keys to avoid duplicate appends."""
    response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!{read_range}",
    ).execute()
    values = response.get("values", [])
    keys = set()
    for row in values[1:]:
        if len(row) <= max(key_columns):
            continue
        keys.add(tuple(str(row[idx]).strip() for idx in key_columns))
    return keys


def format_new_sheet(service, spreadsheet_id: str, sheet_id: int, column_count: int) -> None:
    """Apply basic header formatting once when a sheet is created."""
    requests_body = [
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": column_count,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.07, "green": 0.25, "blue": 0.45},
                        "horizontalAlignment": "CENTER",
                        "textFormat": {
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            "bold": True,
                        },
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)",
            }
        },
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": column_count,
                }
            }
        },
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests_body},
    ).execute()


def append_all_data_rows(
    service,
    spreadsheet_id: str,
    sheet_map: dict[str, int],
    rows: list[dict],
    run_date: str,
) -> int:
    """Append every scanner hit to the master daily history tab."""
    sheet_id, created = ensure_sheet(
        service,
        spreadsheet_id,
        ALL_DATA_SHEET,
        sheet_map,
        len(ALL_DATA_HEADERS),
    )
    if created:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{ALL_DATA_SHEET}'!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [ALL_DATA_HEADERS]},
        ).execute()
        format_new_sheet(service, spreadsheet_id, sheet_id, len(ALL_DATA_HEADERS))

    existing_keys = get_existing_keys(
        service,
        spreadsheet_id,
        ALL_DATA_SHEET,
        "A:C",
        (0, 1, 2),
    )
    values = []
    for row in rows:
        scanner = sanitize_sheet_title(row.get("scanner", "Scanner"))
        symbol = str(row.get("symbol", "")).strip()
        key = (run_date, scanner, symbol)
        if key in existing_keys:
            continue
        values.append([
            run_date,
            scanner,
            symbol,
            row.get("name", ""),
            row.get("price", ""),
            row.get("mcap", ""),
            row.get("pct", ""),
        ])

    if not values:
        log.info(f"{ALL_DATA_SHEET}: added 0 row(s).")
        return 0

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"'{ALL_DATA_SHEET}'!A:G",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()
    log.info(f"{ALL_DATA_SHEET}: added {len(values)} row(s).")
    return len(values)


def append_daily_summary(
    service,
    spreadsheet_id: str,
    sheet_map: dict[str, int],
    grouped: dict[str, list[dict]],
    run_date: str,
) -> int:
    """Append one scanner count row per day to the summary tab."""
    sheet_id, created = ensure_sheet(
        service,
        spreadsheet_id,
        SUMMARY_SHEET,
        sheet_map,
        len(SUMMARY_HEADERS),
    )
    if created:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{SUMMARY_SHEET}'!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [SUMMARY_HEADERS]},
        ).execute()
        format_new_sheet(service, spreadsheet_id, sheet_id, len(SUMMARY_HEADERS))

    existing_keys = get_existing_keys(
        service,
        spreadsheet_id,
        SUMMARY_SHEET,
        "A:B",
        (0, 1),
    )
    values = []
    for scanner, scanner_rows in sorted(grouped.items()):
        key = (run_date, scanner)
        if key in existing_keys:
            continue
        symbols = sorted({str(row.get("symbol", "")).strip() for row in scanner_rows if row.get("symbol")})
        values.append([
            run_date,
            scanner,
            len(symbols),
            ", ".join(symbols),
        ])

    if not values:
        log.info(f"{SUMMARY_SHEET}: added 0 row(s).")
        return 0

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"'{SUMMARY_SHEET}'!A:D",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()
    log.info(f"{SUMMARY_SHEET}: added {len(values)} row(s).")
    return len(values)


def parse_sheet_date(value: str) -> datetime | None:
    """Parse dates already stored in Google Sheets."""
    text = str(value).strip()
    for fmt in ("%d-%b-%Y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def read_all_data_rows(service, spreadsheet_id: str) -> list[dict]:
    """Read the master All_Data sheet and return normalized history rows."""
    response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{ALL_DATA_SHEET}'!A:G",
    ).execute()
    values = response.get("values", [])
    rows = []
    for raw in values[1:]:
        if len(raw) < 3:
            continue
        parsed_date = parse_sheet_date(raw[0])
        if not parsed_date:
            continue
        rows.append({
            "date_text": str(raw[0]).strip(),
            "date": parsed_date,
            "scanner": sanitize_sheet_title(raw[1] if len(raw) > 1 else "Scanner"),
            "symbol": str(raw[2]).strip() if len(raw) > 2 else "",
        })
    return [row for row in rows if row["symbol"]]


def build_year_template_values(rows: list[dict]) -> list[list[object]]:
    """Build screenshot-style columns: date, scanner, then symbols below."""
    grouped: dict[tuple[datetime, str], set[str]] = defaultdict(set)
    for row in rows:
        grouped[(row["date"], row["scanner"])].add(row["symbol"])

    columns = []
    for (date_value, scanner), symbols in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1]), reverse=True):
        columns.append({
            "date": f"{date_value.month}/{date_value.day}/{date_value.year}",
            "scanner": scanner,
            "symbols": sorted(symbols),
        })

    max_symbols = max((len(col["symbols"]) for col in columns), default=0)
    values: list[list[object]] = []
    values.append([col["date"] for col in columns])
    values.append([col["scanner"] for col in columns])
    for idx in range(max_symbols):
        values.append([
            col["symbols"][idx] if idx < len(col["symbols"]) else ""
            for col in columns
        ])
    return values


def clear_sheet(service, spreadsheet_id: str, sheet_name: str) -> None:
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!A:ZZ",
        body={},
    ).execute()


def format_template_sheet(service, spreadsheet_id: str, sheet_id: int, row_count: int, column_count: int) -> None:
    """Apply the yellow/cyan template styling shown in the reference image."""
    if column_count <= 0:
        return
    requests_body = [
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "frozenRowCount": TEMPLATE_HEADER_ROWS,
                        "rowCount": max(row_count, 50),
                        "columnCount": max(column_count, 20),
                    },
                },
                "fields": "gridProperties(frozenRowCount,rowCount,columnCount)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": column_count,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.91, "blue": 0.55},
                        "horizontalAlignment": "RIGHT",
                        "textFormat": {"bold": True, "fontSize": 12},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": column_count,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.29, "green": 0.91, "blue": 0.91},
                        "horizontalAlignment": "LEFT",
                        "textFormat": {"bold": True, "fontSize": 12},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 2,
                    "endRowIndex": max(row_count, 3),
                    "startColumnIndex": 0,
                    "endColumnIndex": column_count,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"fontSize": 12},
                        "horizontalAlignment": "LEFT",
                    }
                },
                "fields": "userEnteredFormat(textFormat,horizontalAlignment)",
            }
        },
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": column_count,
                }
            }
        },
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests_body},
    ).execute()


def rebuild_backtest_template(service, spreadsheet_id: str) -> bool:
    """Create/update one screenshot-style template tab from all rows in All_Data."""
    history = read_all_data_rows(service, spreadsheet_id)
    if not history:
        log.info("No All_Data history found; Backtest_Template skipped.")
        return False

    sheet_map = get_sheet_map(service, spreadsheet_id)
    values = build_year_template_values(history)
    if not values or not values[0]:
        log.info("No template values found; Backtest_Template skipped.")
        return False

    sheet_id, _created = ensure_sheet(service, spreadsheet_id, TEMPLATE_SHEET, sheet_map, len(values[0]))
    clear_sheet(service, spreadsheet_id, TEMPLATE_SHEET)
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{TEMPLATE_SHEET}'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()
    format_template_sheet(service, spreadsheet_id, sheet_id, len(values), len(values[0]))
    log.info(f"Backtest_Template rebuilt with {len(values[0])} column(s).")
    return True


def cleanup_tabs(service, spreadsheet_id: str, active_sheet_names: set[str], sheet_map: dict[str, int]) -> None:
    """Optionally delete tabs outside the compact workbook layout."""
    delete_requests = [
        {"deleteSheet": {"sheetId": sheet_id}}
        for sheet_name, sheet_id in sheet_map.items()
        if sheet_name not in active_sheet_names
    ]
    if not delete_requests:
        return
    if len(delete_requests) >= len(sheet_map):
        delete_requests = delete_requests[:-1]
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": delete_requests},
    ).execute()
    log.info(f"Deleted {len(delete_requests)} stale worksheet(s).")


def upload_to_google_sheets(
    service,
    spreadsheet_id: str,
    rows: list[dict],
    run_date: str,
    cleanup_stale_tabs: bool,
) -> int:
    """Append daily Chartink rows to master and summary tabs."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[sanitize_sheet_title(row.get("scanner", "Scanner"))].append(row)

    sheet_map = get_sheet_map(service, spreadsheet_id)
    if cleanup_stale_tabs:
        cleanup_tabs(service, spreadsheet_id, {ALL_DATA_SHEET, SUMMARY_SHEET, TEMPLATE_SHEET}, sheet_map)
        sheet_map = get_sheet_map(service, spreadsheet_id)

    total_added = append_all_data_rows(service, spreadsheet_id, sheet_map, rows, run_date)
    append_daily_summary(service, spreadsheet_id, sheet_map, grouped, run_date)

    return total_added


def print_dry_run_summary(rows: list[dict], run_date: str) -> None:
    """Print the sheet layout that would be uploaded."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[sanitize_sheet_title(row.get("scanner", "Scanner"))].append(row)

    print(f"Run date: {run_date}")
    print(f"All_Data rows: {len(rows)}")
    print(f"Daily_Summary rows: {len(grouped)}")
    print("Backtest_Template: rebuilt from all All_Data history after upload")
    print("")
    print("Scanner counts:")
    for scanner, scanner_rows in sorted(grouped.items()):
        symbols = sorted({str(row.get("symbol", "")).strip() for row in scanner_rows if row.get("symbol")})
        preview = ", ".join(symbols[:10])
        if len(symbols) > 10:
            preview += f", ... (+{len(symbols) - 10} more)"
        print(f"- {scanner}: {len(symbols)} symbol(s) | {preview}")


def main() -> int:
    args = parse_args()
    if not args.spreadsheet_id:
        log.error("Set GOOGLE_SHEET_ID or pass --spreadsheet-id.")
        return 2

    run_date = args.date or datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%b-%Y")
    if args.template_only:
        service = get_sheets_service(args.credentials)
        rebuilt = rebuild_backtest_template(service, args.spreadsheet_id)
        log.info(f"Template rebuild complete: {'updated' if rebuilt else 'skipped'}")
        if not args.no_open:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{args.spreadsheet_id}/edit"
            log.info(f"Opening Google Sheet: {sheet_url}")
            webbrowser.open(sheet_url)
        return 0

    chartink_login()
    rows = fetch_chartink_dashboard(args.dashboard_url)
    if not rows:
        log.info("No Chartink rows found. Nothing uploaded.")
        return 0

    if args.dry_run:
        print_dry_run_summary(rows, run_date)
        return 0

    service = get_sheets_service(args.credentials)
    added = upload_to_google_sheets(
        service,
        args.spreadsheet_id,
        rows,
        run_date,
        args.cleanup_tabs,
    )
    log.info(f"Upload complete. Total rows added: {added}")
    if not args.no_template:
        rebuilt = rebuild_backtest_template(service, args.spreadsheet_id)
        log.info(f"Template rebuild complete: {'updated' if rebuilt else 'skipped'}")
    if not args.no_open:
        sheet_url = f"https://docs.google.com/spreadsheets/d/{args.spreadsheet_id}/edit"
        log.info(f"Opening Google Sheet: {sheet_url}")
        webbrowser.open(sheet_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

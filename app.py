"""
Cloudflare Cache Purge Action
Purges Cloudflare cache for specified zones using the Cloudflare API.
"""

import requests
import os
import sys

CF_API_URL = "https://api.cloudflare.com/client/v4"


def _get_env_or_none(key: str) -> str | None:
    """Get environment variable, converting empty strings to None."""
    value = os.environ.get(key)
    return None if value == "" else value


CF_EMAIL_ADDR = _get_env_or_none("CF_EMAIL_ADDR")
CF_API_KEY = _get_env_or_none("CF_API_KEY")
CF_ZONE_NAME = _get_env_or_none("CF_ZONE_NAME")
CF_ZONE_NAMES = _get_env_or_none("CF_ZONE_NAMES")
CF_PAGE_COUNT = _get_env_or_none("CF_PAGE_COUNT")
CF_ZONE_ID = _get_env_or_none("CF_ZONE_ID")
CF_ZONE_IDS = _get_env_or_none("CF_ZONE_IDS")


def check_cf_response(response: dict, context: str = "") -> None:
    """Validates Cloudflare API response and raises an error if the request failed."""
    if not response.get("success", False):
        errors = response.get("errors", [])
        messages = response.get("messages", [])
        error_details = []
        for err in errors:
            code = err.get("code", "unknown")
            message = err.get("message", "unknown error")
            error_details.append(f"[{code}] {message}")
        
        error_msg = "Cloudflare API error"
        if context:
            error_msg += f" ({context})"
        error_msg += ": " + "; ".join(error_details) if error_details else ": unknown error"
        
        if messages:
            error_msg += f" | Messages: {messages}"
        
        print(f"Full API response: {response}", file=sys.stderr)
        raise SystemExit(error_msg)


def get_zone_id_by_name(zone_name: str, headers: dict, per_page: str = None) -> str:
    """Fetches Zone ID from Cloudflare API by zone name."""
    page = 1
    per_page_value = per_page if per_page is not None else "20"
    
    while True:
        request_url = f"{CF_API_URL}/zones?per_page={per_page_value}&page={page}"

        try:
            response = requests.get(request_url, headers=headers).json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        
        check_cf_response(response, "fetching zones")
        
        result = response.get("result")
        if result is None:
            raise SystemExit("Cloudflare API returned empty result when fetching zones")

        # Search for zone in current page
        for zone in result:
            if zone["name"] == zone_name:
                return zone["id"]
        
        # Check if there are more pages
        result_info = response.get("result_info", {})
        total_pages = result_info.get("total_pages", 1)
        
        if page >= total_pages:
            # No more pages, zone not found
            break
        
        page += 1
    
    raise SystemExit(f"Zone '{zone_name}' not found in Cloudflare account")


def get_zone_ids_by_names(zone_names: str, headers: dict, per_page: str = None) -> list:
    """Fetches Zone IDs from Cloudflare API by comma-separated zone names."""
    zone_names_list = [name.strip() for name in zone_names.split(",")]
    zone_ids_list = []
    page = 1
    per_page_value = per_page if per_page is not None else "20"
    
    # Continue fetching pages until we find all zones or run out of pages
    while True:
        request_url = f"{CF_API_URL}/zones?per_page={per_page_value}&page={page}"

        try:
            response = requests.get(request_url, headers=headers).json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        check_cf_response(response, "fetching zones")
        
        result = response.get("result")
        if result is None:
            raise SystemExit("Cloudflare API returned empty result when fetching zones")

        # Search for zones in current page
        for zone in result:
            if zone["name"] in zone_names_list:
                zone_ids_list.append(zone["id"])
        
        # If we found all requested zones, we can stop early
        if len(zone_ids_list) == len(zone_names_list):
            break
        
        # Check if there are more pages
        result_info = response.get("result_info", {})
        total_pages = result_info.get("total_pages", 1)
        
        if page >= total_pages:
            # No more pages
            break
        
        page += 1
    
    if not zone_ids_list:
        raise SystemExit(f"None of the zones '{zone_names}' found in Cloudflare account")
    
    return zone_ids_list


def purge_zone_cache(zone_id: str, headers: dict, payload: dict = None) -> None:
    """Purges cache for a single Cloudflare zone."""
    if payload is None:
        payload = {"purge_everything": True}
    
    try:
        response = requests.post(
            f"{CF_API_URL}/zones/{zone_id}/purge_cache",
            headers=headers,
            json=payload
        ).json()
        check_cf_response(response, f"purging cache for zone {zone_id}")
        print(f"Zone ID: {zone_id} - Cache purged successfully.")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def purge_zones_cache(zone_ids: list, headers: dict, payload: dict = None) -> None:
    """Purges cache for multiple Cloudflare zones."""
    if payload is None:
        payload = {"purge_everything": True}
    
    for zone_id in zone_ids:
        try:
            response = requests.post(
                f"{CF_API_URL}/zones/{zone_id}/purge_cache",
                headers=headers,
                json=payload
            ).json()
            check_cf_response(response, f"purging cache for zone {zone_id}")
            print(f"Zone ID: {zone_id} - Cache purged successfully.")
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)


def main() -> None:
    """Main entry point for the Cloudflare cache purge action."""
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": f"{CF_EMAIL_ADDR}",
        "X-Auth-Key": f"{CF_API_KEY}",
        "User-Agent": "github.com/dvlop/cloudflare-purge-actions"
    }

    if CF_ZONE_ID is not None or CF_ZONE_IDS is not None:
        if CF_ZONE_ID is not None:
            purge_zone_cache(CF_ZONE_ID, headers)
        else:
            zone_ids = [zid.strip() for zid in CF_ZONE_IDS.split(",")]
            purge_zones_cache(zone_ids, headers)
    elif CF_ZONE_NAME is not None or CF_ZONE_NAMES is not None:
        if CF_ZONE_NAME is not None:
            zone_id = get_zone_id_by_name(CF_ZONE_NAME, headers, per_page=CF_PAGE_COUNT)
            purge_zone_cache(zone_id, headers)
        else:
            zone_ids = get_zone_ids_by_names(CF_ZONE_NAMES, headers, per_page=CF_PAGE_COUNT)
            purge_zones_cache(zone_ids, headers)
    else:
        raise SystemExit("Error: No zone identifier provided. Set CF_ZONE_ID, CF_ZONE_IDS, CF_ZONE_NAME, or CF_ZONE_NAMES.")


if __name__ == "__main__":
    main()

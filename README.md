# Cloudflare Purge Cache Action

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Cloudflare%20Purge%20Cache-blue?style=flat-square&logo=github)](https://github.com/marketplace/actions/cloudflare-purge-cache)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A GitHub Action to purge Cloudflare cache for your domains. Supports purging by zone name or zone ID, with single or multiple zones.

## Features

- Purge cache by **zone name** (domain) or **zone ID**
- Support for **single zone** or **multiple zones** at once
- Automatic zone ID lookup when using zone names
- Detailed error messages from Cloudflare API
- Lightweight Docker-based action

## Prerequisites

You'll need the following from your Cloudflare account:

1. **Email address** - The email associated with your Cloudflare account
2. **Global API Key** - Found in [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens) under "API Keys" > "Global API Key"

## Usage

### Basic Usage - Purge by Zone Name

```yaml
- name: Purge Cloudflare Cache
  uses: dvlop/cloudflare-purge-actions@v2
  with:
    cf_email: ${{ secrets.CF_EMAIL }}
    cf_api_key: ${{ secrets.CF_API_KEY }}
    cf_zone_name: example.com
```

### Purge by Zone ID

```yaml
- name: Purge Cloudflare Cache
  uses: dvlop/cloudflare-purge-actions@v2
  with:
    cf_email: ${{ secrets.CF_EMAIL }}
    cf_api_key: ${{ secrets.CF_API_KEY }}
    cf_zone_id: ${{ secrets.CF_ZONE_ID }}
```

### Purge Multiple Zones by Name

```yaml
- name: Purge Cloudflare Cache
  uses: dvlop/cloudflare-purge-actions@v2
  with:
    cf_email: ${{ secrets.CF_EMAIL }}
    cf_api_key: ${{ secrets.CF_API_KEY }}
    cf_zone_names: "example.com, example.org, example.net"
```

### Purge Multiple Zones by ID

```yaml
- name: Purge Cloudflare Cache
  uses: dvlop/cloudflare-purge-actions@v2
  with:
    cf_email: ${{ secrets.CF_EMAIL }}
    cf_api_key: ${{ secrets.CF_API_KEY }}
    cf_zone_ids: "zone_id_1, zone_id_2, zone_id_3"
```

### With Custom Page Count

If you have more than 20 zones in your Cloudflare account, increase the page count:

```yaml
- name: Purge Cloudflare Cache
  uses: dvlop/cloudflare-purge-actions@v2
  with:
    cf_email: ${{ secrets.CF_EMAIL }}
    cf_api_key: ${{ secrets.CF_API_KEY }}
    cf_zone_name: example.com
    cf_page_count: "50"
```

## Inputs

| Input | Description | Required |
|-------|-------------|----------|
| `cf_email` | Cloudflare account email address | Yes |
| `cf_api_key` | Cloudflare Global API Key | Yes |
| `cf_zone_name` | Single zone name (domain) to purge | No* |
| `cf_zone_names` | Comma-separated list of zone names | No* |
| `cf_zone_id` | Single Cloudflare Zone ID | No* |
| `cf_zone_ids` | Comma-separated list of Zone IDs | No* |
| `cf_page_count` | Zones per page when fetching (default: 20) | No |

*At least one of `cf_zone_name`, `cf_zone_names`, `cf_zone_id`, or `cf_zone_ids` is required.

## Environment Variables (Legacy)

For backward compatibility, you can also use environment variables directly:

```yaml
- name: Purge Cloudflare Cache
  uses: dvlop/cloudflare-purge-actions@v2
  env:
    CF_EMAIL_ADDR: ${{ secrets.CF_EMAIL }}
    CF_API_KEY: ${{ secrets.CF_API_KEY }}
    CF_ZONE_NAME: example.com
```

| Variable | Description |
|----------|-------------|
| `CF_EMAIL_ADDR` | Cloudflare account email |
| `CF_API_KEY` | Cloudflare Global API Key |
| `CF_ZONE_NAME` | Single zone name |
| `CF_ZONE_NAMES` | Comma-separated zone names |
| `CF_ZONE_ID` | Single Zone ID |
| `CF_ZONE_IDS` | Comma-separated Zone IDs |
| `CF_PAGE_COUNT` | Zones per page (default: 20) |

## Complete Workflow Example

```yaml
name: Deploy and Purge Cache

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Deploy to Production
        run: |
          # Your deployment steps here
          echo "Deploying..."

      - name: Purge Cloudflare Cache
        uses: dvlop/cloudflare-purge-actions@v2
        with:
          cf_email: ${{ secrets.CF_EMAIL }}
          cf_api_key: ${{ secrets.CF_API_KEY }}
          cf_zone_name: ${{ secrets.CF_ZONE_NAME }}
```

## Troubleshooting

### Common Errors

**Authentication error**
- Verify your `CF_EMAIL` and `CF_API_KEY` are correct
- Make sure you're using the Global API Key, not an API Token

**Zone not found**
- Check that the zone name matches exactly (e.g., `example.com`, not `www.example.com`)
- If you have many zones, try increasing `cf_page_count`

**Rate limiting**
- Cloudflare has API rate limits; avoid running this action too frequently

## Acknowledgments

This project is a fork of [cloudflare-purge-actions](https://github.com/Am6puk/cloudflare-purge-actions) by [Andrii Rozhkov](https://github.com/Am6puk).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# NCAA Baseball Data Pipeline

## Overview
Analysts often need NCAA baseball performance data matched to internal player identifiers, but public box score data lacks consistent IDs and requires extensive manual cleanup.

This project is an end-to-end data pipeline that:
- Scrapes NCAA baseball box score data
- Cleans and normalizes player and team statistics
- Resolves players to internal TruMedia IDs via API calls
- Validates and structures the final dataset
- Publishes analyst-ready outputs

The goal is to automate a process that is typically manual, error-prone, and time-consuming.

---

## Pipeline Architecture

Raw NCAA Box Scores  
→ Data Cleaning & Normalization  
→ Player ID Resolution (API)  
→ Data Validation  
→ Export to Google Sheets / CSV  

---

## Key Challenges Solved
- Inconsistent player naming conventions
- Duplicate players across games and teams
- Missing or ambiguous player identifiers
- Ensuring output schema stability for downstream use

---

## Tech Stack
- Python
- pandas
- requests
- BeautifulSoup
- Google Sheets API
- REST API integration

---

## Outputs
- Clean, structured datasets ready for analysis
- Public-facing Google Sheet for stakeholder access
- CSV exports for downstream workflows
- See Output.png

---

## What This Demonstrates
- Real-world data ingestion and cleaning
- API integration and ID resolution logic
- Pipeline thinking and automation
- Delivering usable data products, not just analysis

---

## Notes
Sensitive credentials and internal IDs are anonymized.

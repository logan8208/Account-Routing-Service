"""Shared constants for the account pipeline. Every rule here traces to rules.md or an owner
decision recorded in LOG.md section 3 (cited as D<n>)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_ACCOUNTS = ROOT / "backup_originals" / "accounts-XLSX.xlsx"   # pristine input, never written
RAW_REPS = ROOT / "backup_originals" / "reps-XLSX.xlsx"
ACCOUNTS_XLSX = ROOT / "accounts-XLSX.xlsx"                       # working copy we add columns to
REPS_XLSX = ROOT / "reps-XLSX.xlsx"
OUTPUT = ROOT / "output"

ORIGINAL_COLUMNS = [
    "account_id", "company_name", "website", "country", "city", "state", "employee_count",
    "funding_stage", "last_funding_year", "industry", "existing_spend_usd_t12m", "notes",
]

# rules.md appendix: state/province -> region. Anything else is not covered by this team.
REGION_BY_STATE = {}
for _region, _codes in {
    "EAST": "CT DC DE FL GA IN MA MD ME MI NC NH NJ NY OH PA RI SC VA VT WV NB NL NS ON PE QC",
    "CENTRAL": "AL AR AZ CO IA ID IL KS KY LA MN MO MS MT ND NE NM OK SD TN TX UT WI WY AB MB SK",
    "WEST": "AK CA HI NV OR WA BC",
}.items():
    for _c in _codes.split():
        REGION_BY_STATE[_c] = _region
CANADA_PROVINCES = {"AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK"}
US_STATES = set(REGION_BY_STATE) - CANADA_PROVINCES

# Websites that point at a profile page on someone else's site. They identify nothing about the
# company's own domain, so they are never used for duplicate matching.
PROFILE_HOSTS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "crunchbase.com",
                 "instagram.com"}

MIN_EMPLOYEES = 20            # rules.md: under 20 employees is too small
ENTERPRISE_EMPLOYEES = 500    # rules.md: 500+ or Public / Private Equity
ENTERPRISE_STAGES = {"Public", "Private Equity"}

# --- Note patterns (notes are templated; all 85 distinct notes were read by hand, see LOG.md) ---
# Same legal entity as the named company -> merge into one account (D8).
SAME_ENTITY_NOTE = re.compile(
    r"^(?:Billing domain for|Self-serve signup\. Same company as|Product brand of) (?P<target>[^.;]+?)[.;]")
# Different entity, owned by the named parent -> keep separate, route with the parent (D8).
CHILD_NOTE = re.compile(r"^Business unit of (?P<target>[^.;]+?)\.")
ACQUIRED_NOTE = re.compile(r"^Acquired by (?P<target>.+?) in (?P<year>\d{4})\.")
DEFUNCT_NOTE = re.compile(r"^(Company shut down .+|Domain is parked / for sale\..*)$")
# Core product is a speech engine -> competitor (D10). Notes about building/replacing their own
# STT, internal speech teams, Speech ML job posts, or using a competitor's API are NOT competitors.
COMPETITOR_NOTE = re.compile(
    r"^(Sells its own speech recognition API|Core product is an on-prem ASR engine|"
    r"Speech-to-text vendor; competes with us)")
CHURNED_NOTE = re.compile(r"^Churned (?P<when>\w+ \d{4})\.")
DUPLICATE_Q_NOTE = re.compile(r"^Duplicate\?")
AGENTS_NOTE = re.compile(r"~(?P<n>\d+) agents")

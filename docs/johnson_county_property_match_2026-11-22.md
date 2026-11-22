# Johnson County property-to-investor research — 2026-11-22

**Operating mode: research only.** No real-estate transaction, owner authorization, buyer acceptance, right to market/assign, proof of funds or revenue is established.

## Evidence intake
- Structured source: `data/johnson_county_verified_properties.json`.
- Machine-readable importer: `apex/agents/property_feed.py` (HTTPS listing links, type checks, uniqueness, as-of recency; 7-day expiration).
- Export for an approval queue: `python -m scripts.property_research_report --json`.
- All data is public research and must be re-verified with listing agents and buyer acquisitions teams before transaction proposals.
- `ScoutAgent` can observe fresh research. `AnalystAgent` does not promote properties to qualified deals without contract/title/underwriting evidence. `ExecutorAgent` is non-sending. `MonetizerAgent` never treats offers, invoices, or models as settled revenue.

## Current sourcing and fit

| Property | Public asking price | Type | Buyer candidate / fit | Unresolved |
|---|---:|---|---|---|
| [602 Trinity St](https://www.realtor.com/realestateandhomes-detail/602-Trinity-St_Cleburne_TX_76031_M87680-38411) | $54,900 | 0.523-ac vacant land | [RAW Land & Home](https://rawlandandhome.com/land/criteria): Johnson County, acreage >=0.5, infill accepted, assignments mentioned; **partial match** | Access, utilities, restrictions, title, buyer bid, seller authority, price spread |
| [7112 S Aberdeen Dr](https://www.coldwellbankerhomes.com/tx/cleburne/7112-s-aberdeen-dr/pid_74832472/) | $17,500 | 0.2927-ac vacant land | **RAW EXCLUDED**: below 0.5-ac minimum; other land buyer required | HOA dues, buildability, taxes, disposition value, actual land buyer |
| [833 Carmela Ct](https://www.realtor.com/realestateandhomes-detail/833-Carmela-Ct_Cleburne_TX_76031_M81969-45547) | $160,000 | Rehab house on 2 acres | [BEVA Homes](https://www.bevahomes.com/sell-my-house-fast-cleburne-tx): *category and coverage only*, buy box unverified | Repairs, occupancy (unknown), title, comps, buyer offer |
| [307 N Douglas Ave](https://www.coldwellbankerhomes.com/tx/cleburne/307-n-douglas-ave/pid_74492767/) | $160,000 | Rehab candidate | [New Age House Buying](https://newagehousebuying.com/): *category and coverage only*, buy box unverified | Repairs, occupancy (unknown), comps, buyer offer |

## Priority research sequence (no outreach executed)
1. Re-verify the MLS price and status for 602 Trinity; check Johnson CAD parcel, recorded access, city zoning and utilities. The November 3 Realtor.com listing showed $54,900 / 0.523 acres.
2. Obtain buyer's updated buy box and proof of funds through an approved, separate contact process; the published RAW land criteria are **not** a bid or a contract.
3. For 7112 S Aberdeen, check Retreat HOA and deed restrictions, then search sub-half-acre-lot buyers. Do not send to RAW's >=0.5-acre program.
4. For 833 Carmela and 307 N Douglas, do not classify either as vacant based on listing photos. Verify occupancy and condition with a listing professional before any marketing.
5. Estimate price spread only after actual comparable sales, repairs/holding/closing costs, owner authorization, contract rights and a written investor bid. Default: `profit_verified=false`.

## Legal and operational controls
Texas TREC Rule 535.6 requires written disclosure of equitable interests when assigning a purchase contract without a license. A list of properties you don't control does not authorize marketing them as your inventory or earning an unlicensed brokerage commission. See [TREC rules](https://www.trec.texas.gov/agency-information/rules-and-laws/trec-rules/). Consult a Texas-licensed real estate attorney or broker before attempting an assignment or referral compensation.

No scraping of gated MLS data, no owner-contact enrichment, no invented urgency or vacancy, no unsolicited communication, no purchase agreement, no money movement, and no production deployment are authorized by this research feed.

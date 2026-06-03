Subject: RE: DETECT - Scope Filters Implementation - Clarification Needed

Hi André,

Thank you for your detailed answers regarding the scope filters requirements.

-----

## Current Implementation Status

We have completed the **backend implementation** with the following:

✅ **5 source columns integrated** into the pipeline output:

- `accounting_site_code_post_acc`
- `pmas_code_post_acc`
- `lb_site_risque_apres_accr`
- `business_country`
- `cd_uds_pmas_metier_ap_acc`

✅ **4 pre-defined scope columns** computed as boolean:

- `scope_us`
- `scope_fortis`
- `scope_bcef`
- `scope_japan`

✅ **JSON configuration file** for scope definitions:

- Scope logic is defined in `ccirc_params.json`
- Easy to modify conditions (add/remove site codes, change PMA values, etc.)
- Re-run time: ~30 seconds after config change

-----

## Current Approach (Option A)

Our current implementation follows **Option A**:

|Aspect             |Description                                             |
|-------------------|--------------------------------------------------------|
|**Update method**  |Edit JSON configuration file                            |
|**Who can update** |Data team / Admin                                       |
|**Re-run required**|Yes (~30 seconds)                                       |
|**User experience**|Users select from pre-defined scopes dropdown in Tableau|

**Example JSON config:**

```json
{
  "us": {
    "filters": {
      "accounting_site_code_post_acc": {
        "operator": "IN",
        "values": ["12309", "40043", "11939", ...]
      }
    }
  },
  "bcef": {
    "filters": {
      "pmas_code_post_acc": {"operator": "EQUALS", "value": "PMA_03"},
      "lb_site_risque_apres_accr": {"operator": "NOT_IN", "values": ["BNPP Factor France"]}
    }
  }
}
```

-----

## Clarification Needed

Based on your answer *“the user must be able to update the pre-defined scopes themselves”* and *“needs to be available as user-facing filters”*, I want to clarify:

**Does “update scopes themselves” mean:**

|Option          |User Action                                |Technical Implication                                 |
|----------------|-------------------------------------------|------------------------------------------------------|
|**A** (current) |Request Data team to update JSON config    |Re-run ~30 sec, changes apply to all users            |
|**C** (proposed)|Select filter values directly in Tableau UI|Real-time, each user can create their own custom scope|

-----

## Proposed Enhancement (Option C)

If users need to create custom scopes directly in Tableau **without requesting config changes**, we can implement **Option C**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TABLEAU DASHBOARD                                                          │
│                                                                             │
│  [1] PRE-DEFINED SCOPES (quick selection)                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ○ All  ○ US  ○ Fortis  ○ BCeF  ○ Japan                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [2] CUSTOM FILTERS (user creates their own scope)                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Accounting Site: [Multi-select dropdown ▼]                         │   │
│  │  PMA Code:        [Multi-select dropdown ▼]                         │   │
│  │  LB Site Risque:  [Multi-select dropdown ▼]                         │   │
│  │  Business Country:[Multi-select dropdown ▼]                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  → Users can combine filters to create custom scopes on-the-fly           │
│  → No pipeline re-run needed                                               │
│  → Each user can have their own filter selection                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Option C Benefits:**

- ✅ Pre-defined scopes for common use cases (1-click)
- ✅ Standalone filters for power users (custom scopes)
- ✅ Real-time filtering, no re-run needed
- ✅ Users can adapt filters every quarter without Data team intervention

**Option C is already supported** by our current backend - we just need to configure Tableau to expose the 5 source columns as additional filters.

-----

## Questions

1. **Is Option C the expected behavior?** (users can create custom scopes via Tableau filters)
1. **For the pre-defined scopes (US, Fortis, BCeF, Japan):**
- Should they remain fixed, or should users be able to modify them?
- If modifiable, is JSON config update (Option A) acceptable?
1. **Regarding “save a scope by the user”:**
- Do you mean Tableau’s native “Save Filter” feature?
- Or a custom save mechanism in our system?

Please let me know your preference so we can finalize the Tableau configuration accordingly.

Best regards,
[Your name]

-----

CC: Pierre, Laurent, Team DETECT
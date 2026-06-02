# Oracle SOA Test Migration — Progress

**Project:** oracle_soa_test  
**Source:** `samples/oracle-soa/` (3 sample composites)  
**Target:** Boomi folder **`MIG_oracle_soa_test`** (folderId `Rjo4NTY4NTU1`)  
**Status:** COMPLETE (sample/test run — 2026-05-25)

## Phases

| Phase | Status | Output |
|---|---|---|
| ANALYZE | DONE | `migration-specs/oracle_soa_test.json` |
| ENRICH | SKIPPED | No ANTHROPIC_API_KEY |
| GENERATE | DONE | 6/6 components pushed |
| VALIDATE | DONE | 80% (C) — `oracle_soa_test_review_checklist.md` |

## Components on Platform

| Name | Component ID | Type |
|---|---|---|
| MIG_AccountSyncBPEL | c615d5ae-xxxx | Process |
| MIG_oracle_soa_test_DB_Connection | 8b5ab902-xxxx | Connection |
| MIG_OrderProcessingBPEL_CheckInventory_Operation | 124698bd-xxxx | Operation |
| MIG_OrderProcessingBPEL | 5eb02954-xxxx | Process |
| MIG_NotificationFanoutBPEL_WSSOperation | 4359a68f-xxxx | Operation |
| MIG_NotificationFanoutBPEL | 4435d9a4-xxxx | Process |

## Open Items

- [ ] MEDIUM: `[OrderProcessingBPEL]` ValidateCredit — EBS Adapter mapping needs Oracle EBS connector in account; verify behavior with real integration data
- [ ] MEDIUM: `[NotificationFanoutBPEL]` ParallelNotificationFanout — BPEL `<flow>` is parallel; Boomi Branch is sequential. Verify order-independence of email/DB/EDI routes before approving.

## Notes

This was a test run against synthetic sample composites, not production EBS data. The real EBS migration is tracked separately as `oracle_ebs_migration` once Oracle SOA credentials are configured.

Bugs discovered and fixed during this run (committed in `6b55fdd`):
- Double `MIG_MIG_` prefix in `generate_boomi.py`
- Transform steps over-penalized in `validators/validate_logic.py` (score 30%→80%)

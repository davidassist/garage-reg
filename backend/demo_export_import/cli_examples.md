# GarageReg Data Export/Import CLI Examples

## Export Examples
python data_cli.py export --org-id 1 --format jsonl --output backup_org1.jsonl
python data_cli.py export --org-id 1 --format json --output backup_org1.json  
python data_cli.py export --org-id 1 --format csv --output backup_org1.zip

## Import Examples
python data_cli.py import --file backup_org1.jsonl --format jsonl --org-id 1 --strategy skip --dry-run
python data_cli.py import --file backup_org1.jsonl --format jsonl --org-id 1 --strategy overwrite

## Validation Examples
python data_cli.py validate --file backup_org1.jsonl --format jsonl

## Comparison Examples
python data_cli.py compare --file backup_org1.jsonl --org-id 1 --output diff_report.json

## Round-Trip Test
python data_cli.py round-trip --org-id 1

## List Available Data
python data_cli.py list --type orgs
python data_cli.py list --type tables

# scripts

Use the following command to export tables to CSV file.
```bash
docker exec -it qurtesy_code python3 scripts.py export
```

Use the following command to import data from CSV files into the database.
```bash
docker exec -it qurtesy_code python3 scripts.py import
```

docker exec -it qurtesy_code python3 scripts.py parse_statements
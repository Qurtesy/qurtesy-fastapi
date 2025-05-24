import sys
from _scripts._export import export_data
from _scripts._import import import_data
from _scripts._parse_statements_phonepe import parse_statements_phonepe

if __name__ == "__main__":
    script = sys.argv[1].lower()
    script = sys.argv[1].lower()

    if option == "export":
        export_data()
    elif option == "import":
        import_data()
    elif option == "parse_statements":
        parse_statements_phonepe()
    else:
        print("❌ Invalid option! Use 'export' or 'import'.")
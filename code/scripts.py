import sys
from _scripts._export import export_data
from _scripts._import import import_data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Usage: python script.py <export|import>")
        sys.exit(1)

    option = sys.argv[1].lower()

    if option == "export":
        export_data()
    elif option == "import":
        import_data()
    else:
        print("❌ Invalid option! Use 'export' or 'import'.")
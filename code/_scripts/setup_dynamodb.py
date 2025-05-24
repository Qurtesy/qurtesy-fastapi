import pkgutil
import importlib
import inspect
import models
from pynamodb.models import Model
from config import dynamodb_region, dynamodb_host

def get_all_subclasses(base_class):
    subclasses = set()
    
    # Iterate over all modules inside the 'models' package
    for _, module_name, _ in pkgutil.iter_modules(models.__path__, models.__name__ + "."):
        module = importlib.import_module(module_name)  # Import the module
        
        # Iterate over all classes inside the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, base_class) and obj is not base_class:  # Check if it's a subclass
                subclasses.add(obj)

    return subclasses

def execute_command():
    try:
        for model in get_all_subclasses(Model):
            # Set the host and region
            model.Meta.host = dynamodb_host
            model.Meta.region = dynamodb_region
            # Create the table
            model.create_table(
                read_capacity_units=1,
                write_capacity_units=1
            )
            print(f"{model.Meta.table_name} table is created successfully")
    except Exception as e:
        print("DynamoDB setup failed: %s" % e)

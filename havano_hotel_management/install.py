# File: apps/havano_hotel_management/havano_hotel_management/install.py

import frappe

def before_install():
    """
    Function to run before installing havano_hotel_management app.
    Creates required Customer Group and Item Group that the app depends on.
    """
    print("Creating required groups for Hotel Management System...")
    
    try:
        # Create Hotel Customer Group
        create_hotel_customer_group()
        
        # Create Hotel Item Group  
        create_hotel_item_group()
        
        # Commit changes
        frappe.db.commit()
        print("✓ Successfully created required groups for Hotel Management")
        
    except Exception as e:
        print(f"✗ Error creating required groups: {str(e)}")
        frappe.log_error(f"Hotel Management Installation Error: {str(e)}")
        raise

def create_hotel_customer_group():
    """Create Hotel Customers group if it doesn't exist"""
    customer_group_name = "Hotel Customers"
    
    if not frappe.db.exists("Customer Group", customer_group_name):
        try:
            customer_group = frappe.new_doc("Customer Group")
            customer_group.customer_group_name = customer_group_name
            customer_group.parent_customer_group = "All Customer Groups"
            customer_group.is_group = 0  # Leaf node
            
            # Insert without validation to avoid circular dependency
            customer_group.insert(ignore_permissions=True, ignore_links=True)
            
            print(f"✓ Created Customer Group: {customer_group_name}")
            
        except Exception as e:
            print(f"✗ Failed to create Customer Group '{customer_group_name}': {str(e)}")
            raise
    else:
        print(f"✓ Customer Group '{customer_group_name}' already exists")

def create_hotel_item_group():
    """Create Hotel Rooms item group if it doesn't exist"""
    item_group_name = "Hotel Rooms"
    
    if not frappe.db.exists("Item Group", item_group_name):
        try:
            item_group = frappe.new_doc("Item Group")
            item_group.item_group_name = item_group_name
            item_group.parent_item_group = "All Item Groups"
            item_group.is_group = 0  # Leaf node
            
            # Insert without validation to avoid circular dependency
            item_group.insert(ignore_permissions=True, ignore_links=True)
            
            print(f"✓ Created Item Group: {item_group_name}")
            
        except Exception as e:
            print(f"✗ Failed to create Item Group '{item_group_name}': {str(e)}")
            raise
    else:
        print(f"✓ Item Group '{item_group_name}' already exists")

def after_install():
    """
    Function to run after installing havano_hotel_management app.
    Performs any additional setup required after installation.
    """
    try:
        print("Running post-installation setup for Hotel Management System...")
        
        # Update Hotel Settings if needed
        update_hotel_settings()
        
        # Create default hotel-related items if needed
        create_default_hotel_items()
        
        frappe.db.commit()
        print("✓ Hotel Management System installation completed successfully")
        
    except Exception as e:
        print(f"✗ Post-installation error: {str(e)}")
        frappe.log_error(f"Hotel Management Post-Installation Error: {str(e)}")

def update_hotel_settings():
    """Update Hotel Settings with default values"""
    try:
        if frappe.db.exists("DocType", "Hotel Settings"):
            hotel_settings = frappe.get_single("Hotel Settings")
            
            # Set default customer group if not already set
            if not hotel_settings.get("hotel_customer_group"):
                hotel_settings.hotel_customer_group = "Hotel Customers"
            
            # Set default item group if not already set    
            if not hotel_settings.get("hotel_item_group"):
                hotel_settings.hotel_item_group = "Hotel Rooms"
            
            hotel_settings.save(ignore_permissions=True)
            print("✓ Updated Hotel Settings with default groups")
            
    except Exception as e:
        print(f"✗ Failed to update Hotel Settings: {str(e)}")

def create_default_hotel_items():
    """Create default hotel room types and services"""
    try:
        # Default room types
        room_types = [
            {"name": "Standard Room", "description": "Standard hotel room with basic amenities"},
            {"name": "Deluxe Room", "description": "Deluxe room with enhanced amenities"},
            {"name": "Suite", "description": "Luxury suite with premium amenities"},
        ]
        
        for room_type in room_types:
            item_code = room_type["name"]
            if not frappe.db.exists("Item", item_code):
                item = frappe.new_doc("Item")
                item.item_code = item_code
                item.item_name = item_code
                item.item_group = "Hotel Rooms"
                item.description = room_type["description"]
                item.is_service_item = 1
                item.is_sales_item = 1
                item.is_purchase_item = 0
                item.is_stock_item = 0
                item.insert(ignore_permissions=True)
                print(f"✓ Created default item: {item_code}")
        
    except Exception as e:
        print(f"✗ Failed to create default hotel items: {str(e)}")

# Additional utility functions for cleanup if needed
def before_uninstall():
    """
    Function to run before uninstalling the app.
    Clean up any app-specific data if needed.
    """
    try:
        print("Preparing to uninstall Hotel Management System...")
        # Add any cleanup logic here if needed
        print("✓ Pre-uninstall cleanup completed")
        
    except Exception as e:
        print(f"✗ Pre-uninstall error: {str(e)}")
        frappe.log_error(f"Hotel Management Pre-Uninstall Error: {str(e)}")

def validate_installation():
    """
    Validate that all required components are properly installed
    """
    required_groups = [
        ("Customer Group", "Hotel Customers"),
        ("Item Group", "Hotel Rooms")
    ]
    
    missing_items = []
    for doctype, name in required_groups:
        if not frappe.db.exists(doctype, name):
            missing_items.append(f"{doctype}: {name}")
    
    if missing_items:
        error_msg = f"Installation validation failed. Missing: {', '.join(missing_items)}"
        frappe.throw(error_msg)
        return False
    
    print("✓ Installation validation passed")
    return True
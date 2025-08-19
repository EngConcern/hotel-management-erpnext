import frappe

def after_install():
    """Create default masters required for Havano Hotel Management"""

    # Create Hotel Customers group
    if not frappe.db.exists("Customer Group", "Hotel Customers"):
        cg = frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "Hotel Customers",
            "parent_customer_group": "All Customer Groups",
            "is_group": 0
        })
        cg.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created Customer Group: Hotel Customers")

    # Create Hotel Rooms item group
    if not frappe.db.exists("Item Group", "Hotel Rooms"):
        ig = frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "Hotel Rooms",
            "parent_item_group": "All Item Groups",
            "is_group": 0
        })
        ig.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created Item Group: Hotel Rooms")

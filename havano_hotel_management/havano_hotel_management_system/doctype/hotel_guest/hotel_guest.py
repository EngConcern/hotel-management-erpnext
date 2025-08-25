# Copyright (c) 2025, Alphazen Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class HotelGuest(Document):
	def before_insert(self):
		self.validate_guest_customer()


	def validate_guest_customer(self):
		if not self.guest_customer:
			self.create_customer()

	def create_customer(self):
		try:
			# Check if a Customer already exists for this Guest
			# if not frappe.db.exists("Customer", {"customer_name": self.full_name}):
				# Create a new Customer linked to the Hotel Guest
			hotel_customer_group = frappe.db.get_single_value("Hotel Settings", "hotel_customer_group")

			new_customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": self.full_name,
				"customer_type": "Individual",
				"customer_group": hotel_customer_group,
                "customer_type": "Individual",
                "custom_trade_name": self.full_name,
                "custom_customer_tin": "123456789",
                "custom_customer_vat": "VAT",
                "custom_customer_address": "Harare Zimbabwe",
                "custom_telephone_number": "123456789",
                "custom_province": "Harare",
                "custom_street": "123 Harare St",
                "custom_city": "Harare",
                "custom_house_no": "2000",
                "custom_email_address": "customer@mail.com",
				"territory": "All Territories"
			})
#custom_trade_name, custom_customer_tin, custom_customer_vat, custom_customer_address, custom_telephone_number, custom_province, 
# custom_street, custom_city, custom_house_no, custom_email_address
			# Save the new Customer
			new_customer.insert(ignore_permissions=True)
			# frappe.msgprint(_("Customer created for Guest {0}").format(self.full_name))
			self.guest_customer = new_customer.name

		except Exception as e:
			frappe.log_error(message=str(e), title="Error Creating Customer")
			frappe.throw(_("An error occurred while creating the Customer. Please try again later."))

import frappe

@frappe.whitelist()
def get_guest_ledger(guest):
    if not guest:
        return {"ledger": [], "guest_history": []}
    
    # Query GL Entry table for transactions related to the guest
    ledger_entries = frappe.db.sql("""
        SELECT
            posting_date,
            account,
            debit,
            credit,
            (debit - credit) AS balance,
            voucher_type,
            voucher_no
        FROM
            `tabGL Entry`
        WHERE
            party_type = 'Customer' AND party = %s
        ORDER BY
            posting_date ASC
    """, guest, as_dict=True)
    
    # Get guest history from Reservation, Check In, and Check Out doctypes
    # First, get all reservations for this guest
    reservations = frappe.db.sql("""
        SELECT 
            name as reservation,
            room,
            check_in_date,
            check_out_date
        FROM 
            `tabReservation`
        WHERE 
            guest = %s
        ORDER BY 
            check_in_date DESC
    """, guest, as_dict=True)

    # Get all check-ins for this guest
    check_ins = frappe.db.sql("""
        SELECT 
            name as check_in_id,
            reservation,
            room,
            check_in_date,
            total_charge,
            actual_checkout_date
        FROM 
            `tabCheck In`
        WHERE 
            guest_name = %s
        ORDER BY 
            check_in_date DESC
    """, guest, as_dict=True)

    # Get all check-outs for this guest
    check_outs = frappe.db.sql("""
        SELECT 
            name as check_out_id,
            actual_check_out_time AS check_out_date
        FROM 
            `tabCheck Out`
        WHERE 
            guest = %s
        ORDER BY 
            check_out_date DESC
    """, guest, as_dict=True)

    # Create a comprehensive guest history
    guest_history = []

    # Track which check-ins have been processed
    processed_check_ins = set()

    # Process each reservation and enrich with check-in/check-out data
    for reservation in reservations:
        history_entry = {
            "reservation": reservation.reservation,
            "room": reservation.room,
            "check_in_date": reservation.check_in_date,
            "check_out_date": reservation.check_out_date,
            "status": None,
            "total_amount": None,
            "actual_check_in": None,
            "actual_check_out": None
        }
            
        # Find matching check-in
        for check_in in check_ins:
            if check_in.reservation == reservation.reservation:
                history_entry["actual_check_in"] = check_in.check_in_date
                history_entry["total_amount"] = check_in.total_charge
                history_entry["actual_check_out"] = check_in.actual_checkout_date

                # If check-in has a different room, update it
                if check_in.room and check_in.room != reservation.room:
                    history_entry["room"] = check_in.room
                # Mark this check-in as processed
                processed_check_ins.add(check_in.check_in_id)
                break
            
        # Find matching check-out
        # for check_out in check_outs:
        #     if check_out.reservation == reservation.reservation:
        #         history_entry["actual_check_out"] = check_out.check_out_date
        #         break
            
        # Format dates for display
        if history_entry["check_in_date"]:
            history_entry["check_in_date"] = frappe.utils.formatdate(history_entry["check_in_date"])
        if history_entry["check_out_date"]:
            history_entry["check_out_date"] = frappe.utils.formatdate(history_entry["check_out_date"])
        if history_entry["actual_check_in"]:
            history_entry["actual_check_in"] = frappe.utils.formatdate(history_entry["actual_check_in"])
        if history_entry["actual_check_out"]:
            history_entry["actual_check_out"] = frappe.utils.formatdate(history_entry["actual_check_out"])
            
        # Format amount
        if history_entry["total_amount"]:
            history_entry["total_amount"] = frappe.utils.fmt_money(history_entry["total_amount"])
            
        guest_history.append(history_entry)

    # Now add check-ins that don't have a matching reservation
    for check_in in check_ins:
        if check_in.check_in_id not in processed_check_ins:
            # Create a new history entry for this check-in
            history_entry = {
                "reservation": check_in.reservation or "No Reservation",
                "room": check_in.room,
                "check_in_date": None,  # No planned check-in date
                "check_out_date": None,  # No planned check-out date
                "status": "Walk-in",
                "total_amount": check_in.total_charge,
                "actual_check_in": check_in.check_in_date,
                "actual_check_out": None
            }
            
            # Find matching check-out if any
            for check_out in check_outs:
                if check_out.check_in == check_in.check_in_id:
                    history_entry["actual_check_out"] = check_out.actual_check_out_time
                    break
            
            # Format dates for display
            if history_entry["actual_check_in"]:
                history_entry["actual_check_in"] = frappe.utils.formatdate(history_entry["actual_check_in"])
            if history_entry["actual_check_out"]:
                history_entry["actual_check_out"] = frappe.utils.formatdate(history_entry["actual_check_out"])
            
            # Format amount
            if history_entry["total_amount"]:
                history_entry["total_amount"] = frappe.utils.fmt_money(history_entry["total_amount"])
            
            guest_history.append(history_entry)

    
    # Calculate running balance for each ledger entry
    running_balance = 0
    for entry in ledger_entries:
        running_balance += (entry.debit or 0) - (entry.credit or 0)
        entry.balance = running_balance
            
        # Format numeric values for display
        entry.debit = frappe.utils.fmt_money(entry.debit) if entry.debit else ""
        entry.credit = frappe.utils.fmt_money(entry.credit) if entry.credit else ""
        entry.balance = frappe.utils.fmt_money(entry.balance)
        entry.posting_date = frappe.utils.formatdate(entry.posting_date)
    
    return {
        "ledger": ledger_entries,
        "guest_history": guest_history
    }

# if not guest:
#     return []

# # Query GL Entry table for transactions related to the guest
# ledger_entries = frappe.db.sql("""
#     SELECT
#         posting_date,
#         account,
#         debit,
#         credit,
#         (debit - credit) AS balance,
#         voucher_type,
#         voucher_no
#     FROM
#         `tabGL Entry`
#     WHERE
#         party_type = 'Customer' AND party = %s
#     ORDER BY
#         posting_date ASC
# """, guest, as_dict=True)

# return ledger_entries
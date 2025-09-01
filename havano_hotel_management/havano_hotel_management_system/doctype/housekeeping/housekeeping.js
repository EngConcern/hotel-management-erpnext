// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Housekeeping", {
// 	refresh(frm) {

// 	},
// });

frappe.listview_settings['Housekeeping'] = {
    add_fields: ["room", "cleaning_status", "last_cleaned", "assigned_staff"],
    get_indicator: function (doc) {
        if (doc.cleaning_status === "Clean") {
            return [__("Clean"), "green", "cleaning_status,=,Clean"];
        } else if (doc.cleaning_status === "Dirty") {
            return [__("Dirty"), "red", "cleaning_status,=,Dirty"];
        } else if (doc.cleaning_status === "Out of Order") {
            return [__("Out of Order"), "orange", "cleaning_status,=,Out of Order"];
        }
    }
};
import frappe


def execute():
	frappe.reload_doc("core", "doctype", "notification_count")

	if frappe.db.has_column("Notification Count", "parenttype"):
		frappe.db.sql("""
			UPDATE `tabNotification Count`
			SET reference_doctype = parenttype,
				reference_name = parent,
				docstatus = 0
		""")

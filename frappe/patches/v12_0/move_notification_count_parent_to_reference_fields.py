import frappe


def execute():
	frappe.reload_doc("core", "doctype", "notification_count")
	frappe.db.sql("""
		UPDATE `tabNotification Count`
		SET reference_doctype = parenttype,
			reference_name = parent,
			docstatus = 0
	""")

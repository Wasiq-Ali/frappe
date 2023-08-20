import frappe


def execute():
	frappe.reload_doctype("Contact")

	contacts = frappe.db.sql_list("""
		select name
		from `tabContact`
		where ifnull(middle_name, '') != '' and ifnull(last_name, '') = ''
	""")

	for name in contacts:
		try:
			frappe.get_doc("Contact", name).save(ignore_permissions=True)
			frappe.db.commit()
		except frappe.ValidationError:
			frappe.db.rollback()

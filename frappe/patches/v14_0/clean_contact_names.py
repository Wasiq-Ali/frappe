import frappe


def execute():
	contacts = frappe.db.sql_list("""
		select name
		from `tabContact`
		where ifnull(middle_name, '') != '' and ifnull(last_name, '') = ''
	""")

	for name in contacts:
		frappe.get_doc("Contact", name).save(ignore_permissions=True)

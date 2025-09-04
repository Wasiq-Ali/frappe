import frappe


def execute():
	frappe.db.sql("""
		delete from `tabLogs To Clear`
		where ref_doctype = 'Integration Request' and parenttype = 'Log Settings'
	""")

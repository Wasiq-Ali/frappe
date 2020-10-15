import frappe

def execute():
	todos = frappe.get_all("ToDo", filters={'title': ['is', 'not set']})
	for d in todos:
		doc = frappe.get_doc("ToDo", d.name)
		doc.set_title()
		doc.db_set('title', doc.title)
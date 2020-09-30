import frappe

def execute():
    doc_type_list = frappe.db.sql_list("""select distinct document_type from `tabAuto Value Setter`""")
	
    for doc_type in  doc_type_list:
        frappe.make_property_setter({
            'doctype': doc_type,
            'doctype_or_field': 'DocType',
            'property': 'allow_auto_value_setter',
            'property_type': 'Check',
            'value': 1
        })
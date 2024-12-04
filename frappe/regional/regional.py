import frappe
from frappe import _


def validate_mobile_no(mobile_no, throw=True):
	if frappe.db.get_default("country") == 'Pakistan':
		from frappe.regional.pakistan import validate_mobile_pakistan
		return validate_mobile_pakistan(mobile_no, throw=throw)
	elif frappe.db.get_default("country") == 'United Arab Emirates':
		from frappe.regional.uae import validate_mobile_uae
		return validate_mobile_uae(mobile_no, throw=throw)
	else:
		return bool(mobile_no)


@frappe.whitelist()
def validate_duplicate_tax_id(doctype, fieldname, value, exclude=None, throw=False):
	if not value:
		return

	meta = frappe.get_meta(doctype)
	if not fieldname or not meta.has_field(fieldname):
		frappe.throw(_("Invalid fieldname {0}").format(fieldname))

	label = _(meta.get_field(fieldname).label)

	filters = {fieldname: value}
	if exclude:
		filters['name'] = ['!=', exclude]

	duplicates = frappe.db.get_all(doctype, filters=filters)
	duplicate_names = [d.name for d in duplicates]
	if duplicates:
		frappe.msgprint(_("{0} {1} is already set in {2}: {3}").format(label, frappe.bold(value), doctype,
			", ".join([frappe.utils.get_link_to_form(doctype, name) for name in duplicate_names])),
			raise_exception=throw, indicator='red' if throw else 'orange')

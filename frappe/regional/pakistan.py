import frappe
from frappe import _
import re

cnic_regex = re.compile(r'^.....-.......-.$')
ntn_regex = re.compile(r'^.......-.$')
strn_regex = re.compile(r'^..-..-....-...-..$')

mobile_regex = re.compile(r'^03\d\d-\d\d\d\d\d\d\d$')


def validate_ntn_cnic_strn(ntn=None, cnic=None, strn=None):
	if frappe.db.get_default("country") != 'Pakistan':
		return

	if ntn and not ntn_regex.match(ntn):
		frappe.throw(_("Invalid NTN. NTN must be in the format #######-#"))
	if cnic and not cnic_regex.match(cnic):
		frappe.throw(_("Invalid CNIC. CNIC must be in the format #####-#######-#"))
	if strn and not strn_regex.match(strn):
		frappe.throw(_("Invalid STRN. STRN must be in the format ##-##-####-###-##"))


def validate_mobile_pakistan(mobile_no, throw=True):
	if frappe.db.get_default("country") != 'Pakistan':
		return True

	if not mobile_no:
		return False

	# do not check mobile number validity for international numbers
	if mobile_no[:1] == "+" or mobile_no[:2] == "00":
		return True

	if not mobile_regex.match(mobile_no):
		if throw:
			frappe.throw(_("Invalid Mobile No. Pakistani Mobile Nos must be in the format 03##-#######"))

		return False

	return True


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

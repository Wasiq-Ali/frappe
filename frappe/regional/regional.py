import frappe
from frappe import _
from frappe.utils import cstr


def validate_mobile_no(mobile_no, throw=True):
	if frappe.db.get_default("country") == 'Pakistan':
		from frappe.regional.pakistan import validate_mobile_pakistan
		return validate_mobile_pakistan(mobile_no, throw=throw)
	elif frappe.db.get_default("country") == 'United Arab Emirates':
		from frappe.regional.uae import validate_mobile_uae
		return validate_mobile_uae(mobile_no, throw=throw)
	else:
		return bool(mobile_no)


def validate_tax_ids(tax_id=None, tax_cnic=None, tax_strn=None):
	if frappe.db.get_default("country") == 'Pakistan':
		from frappe.regional.pakistan import validate_tax_ids_pakistan
		return validate_tax_ids_pakistan(tax_id=tax_id, tax_cnic=tax_cnic, tax_strn=tax_strn)
	elif frappe.db.get_default("country") == 'United Arab Emirates':
		from frappe.regional.uae import validate_tax_ids_uae
		return validate_tax_ids_uae(tax_id=tax_id, tax_cnic=tax_cnic)
	else:
		return


@frappe.whitelist()
def validate_duplicate_tax_id(doctype, fieldname, value, exclude=None, throw=False):
	value = cstr(value).strip()
	if not value:
		return

	validate_duplicate_value(doctype, fieldname, value, exclude, throw)


@frappe.whitelist()
def validate_duplicate_mobile_no(doctype, fieldname, value, exclude=None, throw=False):
	value = cstr(value).strip()
	if not value:
		return
	if not validate_mobile_no(value, throw=False):
		return

	values = [value]

	international_prefix = mobile_international_prefix()
	local_prefix = mobile_local_prefix()

	# Internatinoal to Local
	is_international_number = False
	if international_prefix and local_prefix is not None:
		if value.startswith(f"00{international_prefix}"):
			is_international_number = True
			base_number = value[len(international_prefix) + 2:]
			values.append(f"{local_prefix}{base_number}")
		elif value.startswith(f"+{international_prefix}"):
			is_international_number = True
			base_number = value[len(international_prefix) + 1:]
			values.append(f"{local_prefix}{base_number}")

	# Local to International
	if local_prefix is not None and international_prefix and not is_international_number:
		if local_prefix:
			if value.startswith(local_prefix):
				base_number = value[len(local_prefix):]
				values.append(f"+{international_prefix}{base_number}")
				values.append(f"00{international_prefix}{base_number}")
		else:
			base_number = value
			values.append(f"+{international_prefix}{base_number}")
			values.append(f"00{international_prefix}{base_number}")

	validate_duplicate_value(doctype, fieldname, values, exclude, throw)


def validate_duplicate_value(doctype, fieldname, value, exclude=None, throw=False):
	if not value or not doctype:
		return

	meta = frappe.get_meta(doctype)
	if not fieldname or not meta.has_field(fieldname):
		frappe.throw(_("Invalid fieldname {0}").format(fieldname))

	frappe.has_permission(doctype, "read", throw=True)

	label = _(meta.get_field(fieldname).label)

	filters = {}
	if isinstance(value, (list, tuple)):
		filters[fieldname] = ["in", value]
	else:
		filters[fieldname] = value

	if exclude:
		filters['name'] = ['!=', exclude]

	duplicates = frappe.db.get_all(doctype, filters=filters, fields=["name", fieldname])
	duplicate_names = [d.name for d in duplicates]
	duplicate_values = list(set([d.get(fieldname) for d in duplicates]))
	duplicate_values = ", ".join(duplicate_values)
	if duplicates:
		frappe.msgprint(_("{0} {1} is already set in {2}: {3}").format(label, frappe.bold(duplicate_values), doctype,
			", ".join([frappe.utils.get_link_to_form(doctype, name) for name in duplicate_names])),
			raise_exception=throw, indicator='red' if throw else 'orange')


def mobile_local_prefix():
	if frappe.db.get_default("country") == 'Pakistan':
		from frappe.regional.pakistan import mobile_local_prefix
		return mobile_local_prefix
	elif frappe.db.get_default("country") == 'United Arab Emirates':
		from frappe.regional.uae import mobile_local_prefix
		return mobile_local_prefix


def mobile_international_prefix():
	if frappe.db.get_default("country") == 'Pakistan':
		from frappe.regional.pakistan import mobile_international_prefix
		return mobile_international_prefix
	elif frappe.db.get_default("country") == 'United Arab Emirates':
		from frappe.regional.uae import mobile_international_prefix
		return mobile_international_prefix

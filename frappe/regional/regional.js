frappe.provide("frappe.regional");

import "./pakistan.js";
import "./uae.js";

Object.assign(frappe.regional, {
	format_mobile_no: function (frm, fieldname) {
		let value = frm.doc[fieldname];
		if (value) {
			value = frappe.regional.get_formatted_mobile_no(value);
			frm.doc[fieldname] = value;
			frm.refresh_field(fieldname);
		}
	},

	get_formatted_mobile_no: function (value) {
		if (frappe.sys_defaults.country == "Pakistan") {
			return frappe.regional.pakistan.get_formatted_mobile_no(value);
		} else if (frappe.sys_defaults.country == "United Arab Emirates") {
			return frappe.regional.uae.get_formatted_mobile_no(value);
		} else {
			return value;
		}
	},

	validate_duplicate_tax_id: function (doc, fieldname) {
		let value = doc[fieldname];
		if (value) {
			return frappe.call({
				method: "frappe.regional.regional.validate_duplicate_tax_id",
				args: {
					doctype: doc.doctype,
					fieldname: fieldname,
					value: value,
					exclude: doc.__islocal ? null : doc.name
				}
			});
		}
	},
});

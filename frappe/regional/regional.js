frappe.provide("frappe.regional");

import "./pakistan.js";
import "./uae.js";

Object.assign(frappe.regional, {
	get_formatted_mobile_no: function (value) {
		if (frappe.sys_defaults.country == "Pakistan") {
			return frappe.regional.pakistan.get_formatted_pak_mobile_no(value);
		} else if (frappe.sys_defaults.country == "United Arab Emirates") {
			return frappe.regional.uae.get_formatted_uae_mobile_no(value);
		} else {
			return value;
		}
	},

	format_mobile_no: function (frm, fieldname) {
		if (frappe.sys_defaults.country != 'Pakistan' && frappe.sys_defaults.country != 'United Arab Emirates') {
			return
		}

		let value = frm.doc[fieldname]
		if (value) {
			value = frappe.regional.get_formatted_mobile_no(value);
			frm.doc[fieldname] = value;
			frm.refresh_field(fieldname);
		}
	}

});

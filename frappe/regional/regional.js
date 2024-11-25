frappe.provide("frappe.regional");

import "./pakistan.js";
import "./uae.js";

Object.assign(frappe.regional, {
	get_formatted_mobile_nos : function(value){
		if (frappe.sys_defaults.country == "Pakistan") {
			return frappe.regional.pakistan.get_formatted_mobile_no(value);
		}
		else if (frappe.sys_defaults.country == "United Arab Emirates") {
			return frappe.regional.uae.get_formatted_uae_mobile_no(value);
		}
		else {
			return Boolean(value)
		}

	}

});

frappe.provide("frappe.regional.uae");

Object.assign(frappe.regional.uae, {
	get_formatted_uae_mobile_no: function (value) {
		if (frappe.sys_defaults.country != "United Arab Emirates") {
			return value;
		}

		value = value.replace(/[^0-9+]+/g, "");

		// do not format international numbers
		if (
			value.slice(0, 1) === '+' && value.slice(0, 4) === '+971' ||
			value.slice(0, 2) === '00' && value.slice(0, 5) === '00971'
		) {
			return value;
		}

		return value;
	}
});
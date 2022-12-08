frappe.ui.form.ControlDatetime = frappe.ui.form.ControlDate.extend({
	set_date_options: function() {
		this._super();
		this.today_text = __("Now");
		this.date_format = frappe.defaultDatetimeFormat;

		var time_hour_format = frappe.datetime.get_time_hour_format();
		var time_format = time_hour_format == "12 Hour" ? "hh:ii:ss AA" : "hh:ii:ss";

		$.extend(this.datepicker_options, {
			timepicker: true,
			timeFormat: time_format,
			onSelect: () => {
				// ignore micro seconds
				if (moment(this.get_value()).format(frappe.defaultDatetimeFormat) != moment(this.value).format(frappe.defaultDatetimeFormat)) {
					this.$input.trigger('change');
				}
			},
		});
	},
	get_now_date: function() {
		return frappe.datetime.now_datetime(true);
	},
	set_description: function() {
		const { description } = this.df;
		const { time_zone } = frappe.sys_defaults;
		if (!frappe.datetime.is_timezone_same()) {
			if (!description) {
				this.df.description = time_zone;
			} else if (!description.includes(time_zone)) {
				this.df.description += '<br>' + time_zone;
			}
		}
		this._super();
	}
});

// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for license information please see license.txt

frappe.provide("frappe.form.formatters");

frappe.form.link_formatters = {};

frappe.form.formatters = {
	_style: function(value, df, options, right_align) {
		if (options && (options.inline || options.only_value)) {
			return value;
		} else {
			value = frappe.form.formatters._apply_custom_formatter(value, df, options);

			if (options) {
				var css = "";

				if (options.css && !$.isEmptyObject(options.css)) {
					$.each(options.css || {}, function (prop, val) {
						css += `${prop}:${val};`;
					});
				}

				if (options.link_href) {
					value = `<a href='${options.link_href}' title="${options.link_title || "Open Link"}"`
						+ (options.link_target ? ` target='${options.link_target}'` : "")
						+ (css ? ` style='${css}'` : "")
						+ `>${value}</a>`;

					css = "";
				}
			}

			if (css || right_align) {
				right_align = right_align ? 'text-align: right;' : '';
				css = ` style='${cstr(css)}${right_align}'`;
				return `<div${css}>${value}</div>`;
			} else {
				return value;
			}
		}
	},

	_apply_custom_formatter: function (value, df, options) {
		/* you can add a custom formatter in df.formatter
		example:
			frappe.meta.docfield_map[df.parent][df.fieldname].formatter = (value) => {
				if (value==='Test') return '😜';
			}
		*/

		if (df) {
			const std_df =
				frappe.meta.docfield_map[df.parent] &&
				frappe.meta.docfield_map[df.parent][df.fieldname];
			if (std_df && std_df.formatter && typeof std_df.formatter === "function") {
				value = std_df.formatter(value, df);
			}
		}
		return value;
	},

	_format_number: function(value, format, precision) {
		return (value == null || value === "") ? "" : format_number(value, format, precision);
	},

	Data: function(value, df, options) {
		if (df && df.options == "URL") {
			return `<a href="${value}" title="Open Link" target="_blank">${value}</a>`;
		}
		value = value == null ? "" : value;

		return frappe.form.formatters._style(value, df, options);
	},
	Autocomplete: function (value, df, options) {
		return __(frappe.form.formatters["Data"](value, df, options));
	},
	Select: function (value, df, options) {
		return __(frappe.form.formatters["Data"](value, df, options));
	},
	Float: function (value, docfield, options, doc) {
		// don't allow 0 precision for Floats, hence or'ing with null
		let precision = docfield.precision
			|| cint(frappe.boot.sysdefaults && frappe.boot.sysdefaults.float_precision)
			|| null;

		if (docfield.options && docfield.options.trim()) {
			// options points to a currency field, but expects precision of float!
			docfield.precision = precision;
			return frappe.form.formatters.Currency(value, docfield, options, doc);
		} else {
			// show 1.000000 as 1
			if (!(options || {}).always_show_decimals && !is_null(value)) {
				let temp = cstr(flt(value, precision)).split(".");
				if (temp[1] == undefined || cint(temp[1]) === 0) {
					precision = 0;
				}
			}

			value = frappe.form.formatters._format_number(value, null, precision);

			return frappe.form.formatters._style(value, docfield, options, true);
		}
	},
	Int: function(value, docfield, options) {
		value = frappe.form.formatters._format_number(value, null, 0);
		return frappe.form.formatters._style(value, docfield, options, true);
	},
	Percent: function(value, docfield, options) {
		if (value == null || value === "")
			value = "";
		else {
			value = flt(value, 2) + "%";
		}

		return frappe.form.formatters._style(value, docfield, options, true);
	},
	Rating: function (value, docfield) {
		let rating_html = "";
		let number_of_stars = docfield.options || 5;
		value = value * number_of_stars;
		value = Math.round(value * 2) / 2; // roundoff number to nearest 0.5
		Array.from({ length: cint(number_of_stars) }, (_, i) => i + 1).forEach((i) => {
			rating_html += `<svg class="icon icon-md" data-rating=${i} viewBox="0 0 24 24" fill="none">
				<path class="right-half ${
					i <= (value || 0) ? "star-click" : ""
				}" d="M11.9987 3.00011C12.177 3.00011 12.3554 3.09303 12.4471 3.27888L14.8213 8.09112C14.8941 8.23872 15.0349 8.34102 15.1978 8.3647L20.5069 9.13641C20.917 9.19602 21.0807 9.69992 20.7841 9.9892L16.9421 13.7354C16.8243 13.8503 16.7706 14.0157 16.7984 14.1779L17.7053 19.4674C17.7753 19.8759 17.3466 20.1874 16.9798 19.9945L12.2314 17.4973C12.1586 17.459 12.0786 17.4398 11.9987 17.4398V3.00011Z" fill="var(--star-fill)" stroke="var(--star-fill)"/>
				<path class="left-half ${
					i <= (value || 0) || i - 0.5 == value ? "star-click" : ""
				}" d="M11.9987 3.00011C11.8207 3.00011 11.6428 3.09261 11.5509 3.27762L9.15562 8.09836C9.08253 8.24546 8.94185 8.34728 8.77927 8.37075L3.42887 9.14298C3.01771 9.20233 2.85405 9.70811 3.1525 9.99707L7.01978 13.7414C7.13858 13.8564 7.19283 14.0228 7.16469 14.1857L6.25116 19.4762C6.18071 19.8842 6.6083 20.1961 6.97531 20.0045L11.7672 17.5022C11.8397 17.4643 11.9192 17.4454 11.9987 17.4454V3.00011Z" fill="var(--star-fill)" stroke="var(--star-fill)"/>
			</svg>`;
		});
		return `<div class="rating">
			${rating_html}
		</div>`;
	},
	Currency: function (value, docfield, options, doc) {
		var currency = frappe.meta.get_field_currency(docfield, doc);
		var precision = docfield.precision
			|| cint(frappe.boot.sysdefaults && frappe.boot.sysdefaults.float_precision)
			|| 2;

		// If you change anything below, it's going to hurt a company in UAE, a bit.
		if (precision > 2) {
			var parts = cstr(value).split("."); // should be minimum 2, comes from the DB
			var decimals = parts.length > 1 ? parts[1] : ""; // parts.length == 2 ???

			if (decimals.length < 3 || decimals.length < precision) {
				const fraction =
					frappe.model.get_value(":Currency", currency, "fraction_units") || 100; // if not set, minimum 2.

				if (decimals.length < cstr(fraction).length) {
					precision = cstr(fraction).length - 1;
				}
			}
		}

		value = (value == null || value === "")
			? "" : format_currency(value, currency, precision, cint(docfield.force_currency_symbol));

		if (options && options.only_value) {
			return value;
		} else {
			return frappe.form.formatters._style(value, docfield, options, true);
		}
	},
	Check: function (value) {
		return `<input type="checkbox" disabled
			class="disabled-${value ? "selected" : "deselected"}">`;
	},
	Link: function (value, docfield, options, doc) {
		var doctype = docfield._options || docfield.options;
		var original_value = value;
		let link_title = frappe.utils.get_link_title(doctype, value);

		if (value && value.match && value.match(/^['"].*['"]$/)) {
			value.replace(/^.(.*).$/, "$1");
		}

		if (options && (options.for_print || options.only_value)) {
			return link_title || value;
		}

		if (frappe.form.link_formatters[doctype]) {
			// don't apply formatters in case of composite (parent field of same type)
			if (doc && doctype !== doc.doctype) {
				value = frappe.form.link_formatters[doctype](value, doc, docfield);
			}
		}

		if (!value) {
			return "";
		}
		if (value[0] == "'" && value[value.length - 1] == "'") {
			return value.substring(1, value.length - 1);
		}

		var color_style = "";
		if (options && options.css && typeof options.css === 'object' && options.css.color) {
			color_style = `style="color: ${options.css.color}"`;
		}

		var css_class = [];
		if (options && options.indicator) {
			css_class.push(`indicator ${options.indicator}`);
		}

		var anchor;
		if (docfield && docfield.link_onclick) {
			anchor = repl('<a onclick="%(onclick)s" ${color_style}>%(value)s</a>', {
				onclick: docfield.link_onclick.replace(/"/g, "&quot;"),
				value: value,
			});
		} else if (docfield && doctype) {
			if (frappe.model.can_read(doctype)) {
				anchor = `<a class="${css_class.join(' ')}" ${color_style}
					href="/app/${encodeURIComponent(frappe.router.slug(doctype))}/${encodeURIComponent(
					original_value
				)}"
					data-doctype="${doctype}"
					data-name="${original_value}"
					data-value="${original_value}">
					${__((options && options.label) || link_title || value)}</a>`;
			} else {
				 anchor = link_title || value;
			}
		} else {
			anchor = link_title || value;
		}

		return frappe.form.formatters._style(anchor, docfield, options);
	},
	Date: function (value, docfield, options) {
		if (!frappe.datetime.str_to_user) {
			return value;
		}
		if (value) {
			value = frappe.datetime.str_to_user(value);
			// handle invalid date
			if (value === "Invalid date") {
				value = null;
			}
		}

		value = value || "";
		return frappe.form.formatters._style(value, docfield, options);
	},
	DateRange: function (value, docfield, options) {
		if (Array.isArray(value)) {
			value = __("{0} to {1}", [
				frappe.datetime.str_to_user(value[0]),
				frappe.datetime.str_to_user(value[1]),
			]);
		} else {
			value = value || "";
		}

		return frappe.form.formatters._style(value, docfield, options);
	},
	Datetime: function(value, docfield, options) {
		if(value) {
			var m = moment(frappe.datetime.convert_to_user_tz(value));
			value = m.format(frappe.datetime.get_user_date_fmt().toUpperCase() + ', ' + frappe.datetime.get_user_time_fmt());
		} else {
			value = "";
		}

		return frappe.form.formatters._style(value, docfield, options);
	},
	Text: function(value, df, options) {
		if(value) {
			var tags = ["<p", "<div", "<br", "<table"];
			var match = false;

			for (var i = 0; i < tags.length; i++) {
				if (value.match(tags[i])) {
					match = true;
					break;
				}
			}

			if(!match && (!options || !options.no_newlines)) {
				value = frappe.utils.replace_newlines(value);
			}
		}

		return frappe.form.formatters.Data(value, df, options);
	},
	Time: function (value, docfield, options) {
		if (value) {
			value = frappe.datetime.str_to_user(value, true);
		} else {
			value = "";
		}

		return frappe.form.formatters._style(value, docfield, options);
	},
	Duration: function (value, docfield, options) {
		if (value) {
			let duration_options = frappe.utils.get_duration_options(docfield);
			value = frappe.utils.get_formatted_duration(value, duration_options);
		}

		value = value || "0s";

		return frappe.form.formatters._style(value, docfield, options);
	},
	LikedBy: function (value) {
		var html = "";
		$.each(JSON.parse(value || "[]"), function (i, v) {
			if (v) html += frappe.avatar(v);
		});
		return html;
	},
	Tag: function (value) {
		var html = "";
		$.each((value || "").split(","), function (i, v) {
			if (v)
				html += `
				<span
					class="data-pill btn-xs align-center ellipsis"
					style="background-color: var(--control-bg); box-shadow: none; margin-right: 4px;"
					data-field="_user_tags" data-label="${v}'">
					${v}
				</span>`;
		});
		return html;
	},
	Comment: function (value) {
		return value;
	},
	Assign: function (value) {
		var html = "";
		$.each(JSON.parse(value || "[]"), function (i, v) {
			if (v)
				html +=
					'<span class="label label-warning" \
				style="margin-right: 7px;"\
				data-field="_assign">' +
					v +
					"</span>";
		});
		return html;
	},
	SmallText: function(value, docfield, options) {
		return frappe.form.formatters.Text(value, docfield, options);
	},
	TextEditor: function (value) {
		let formatted_value = frappe.form.formatters.Text(value);
		// to use ql-editor styles
		try {
			if (
				!$(formatted_value).find(".ql-editor").length &&
				!$(formatted_value).hasClass("ql-editor")
			) {
				formatted_value = `<div class="ql-editor read-mode">${formatted_value}</div>`;
			}
		} catch (e) {
			formatted_value = `<div class="ql-editor read-mode">${formatted_value}</div>`;
		}

		return formatted_value;
	},
	Code: function (value) {
		return "<pre>" + (value == null ? "" : $("<div>").text(value).html()) + "</pre>";
	},
	WorkflowState: function (value) {
		var workflow_state = frappe.get_doc("Workflow State", value);
		if (workflow_state) {
			return repl(
				"<span class='label label-%(style)s' \
				data-workflow-state='%(value)s'\
				style='padding-bottom: 4px; cursor: pointer;'>\
				<i class='fa fa-small fa-white fa-%(icon)s'></i> %(value)s</span>",
				{
					value: value,
					style: workflow_state.style.toLowerCase(),
					icon: workflow_state.icon,
				}
			);
		} else {
			return "<span class='label'>" + value + "</span>";
		}
	},
	Email: function (value) {
		return $("<div></div>").text(value).html();
	},
	FileSize: function (value) {
		if (value > 1048576) {
			value = flt(flt(value) / 1048576, 1) + "M";
		} else if (value > 1024) {
			value = flt(flt(value) / 1024, 1) + "K";
		}
		return value;
	},
	TableMultiSelect: function (rows, df, options) {
		rows = rows || [];
		const meta = frappe.get_meta(df.options);
		const link_field = meta.fields.find((df) => df.fieldtype === "Link");
		const formatted_values = rows.map((row) => {
			const value = row[link_field.fieldname];
			return frappe.format(value, link_field, options, row);
		});
		return formatted_values.join(", ");
	},
	Color: (value) => {
		return value
			? `<div>
			<div class="selected-color" style="background-color: ${value}"></div>
			<span class="color-value">${value}</span>
		</div>`
			: "";
	},
	Icon: (value) => {
		return value
			? `<div>
			<div class="selected-icon">${frappe.utils.icon(value, "md")}</div>
			<span class="icon-value">${value}</span>
		</div>`
			: "";
	},
};

frappe.form.get_formatter = function (fieldtype) {
	if (!fieldtype) fieldtype = "Data";
	return frappe.form.formatters[fieldtype.replace(/ /g, "")] || frappe.form.formatters.Data;
};

frappe.format = function (value, df, options, doc) {
	if (!df) df = { fieldtype: "Data" };
	if (df.fieldname == "_user_tags") df.fieldtype = "Tag";
	var fieldtype = df.fieldtype || "Data";

	// format Dynamic Link as a Link
	if (fieldtype === "Dynamic Link") {
		fieldtype = "Link";
		df._options = doc ? doc[df.options] : null;
	}

	var formatter = df.formatter || frappe.form.get_formatter(fieldtype);

	var formatted = formatter(value, df, options, doc);

	if (typeof formatted == "string") formatted = frappe.dom.remove_script_and_style(formatted);

	return formatted;
};

frappe.get_format_helper = function (doc) {
	var helper = {
		get_formatted: function (fieldname) {
			var df = frappe.meta.get_docfield(doc.doctype, fieldname);
			if (!df) {
				console.log("fieldname not found: " + fieldname);
			}
			return frappe.format(doc[fieldname], df, { inline: 1 }, doc);
		},
	};
	$.extend(helper, doc);
	return helper;
};

frappe.form.link_formatters["User"] = function (value, doc, docfield) {
	let full_name = doc && (doc.full_name || (docfield && doc[`${docfield.fieldname}_full_name`]));
	return full_name || value;
};

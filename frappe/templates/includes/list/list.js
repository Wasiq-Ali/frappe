window.list_view = {
	next_start: {{ next_start or 0 }},
	loading: false,

	events: {
		on_reload: [],
		on_load_more: [],
	},

	bind_on_reload: function(callback) {
		list_view._bind_event("on_reload", callback);
	},
	trigger_on_reload: function(r) {
		list_view._trigger_event("on_reload", r);
	},

	bind_on_load_more: function(callback) {
		list_view._bind_event("load_more", callback);
	},
	trigger_on_load_more: function(r) {
		list_view._trigger_event("load_more", r);
	},

	_bind_event: function(event, callback) {
		if (event && callback) {
			if (!list_view.events[event]) {
				list_view.events[event] = [];
			}
			list_view.events[event].push(callback);
		}
	},
	_trigger_event: function(event, r) {
		for (let callback of list_view.events[event] || []) {
			callback(r);
		}
	},
}

$.extend(list_view, {
	bind_events: function() {
		$(".website-list .btn-more").on("click", function() {
			let btn = $(this);
			return list_view.load_more(btn);
		});

		if($('.navbar-header .navbar-toggle:visible').length === 1) {
			$('.page-head h1').addClass('list-head').click(function(){
				window.history.back();
			 });
		}
	},

	reload: function(opts) {
		if (list_view.loading) {
			return;
		}

		if (!opts) {
			opts = {};
		}

		let args = list_view.get_query_args();

		list_view.set_is_loading(true, opts.btn);

		return $.ajax({
			url: "/api/method/frappe.www.list.get",
			data: args,
			statusCode: {
				200: function(r) {
					list_view.next_start = r.message.next_start;

					list_view.clear_list();
					list_view.append_list(r.message.result);
					list_view.toggle_show_more_button(r.message.show_more);
					list_view.toggle_empty_result(!r.message.result.length);

					list_view.trigger_on_reload(r);
					opts.callback && opts.callback(r);
				}
			}
		}).always(function() {
			list_view.set_is_loading(false, opts.btn);
		});
	},

	load_more: function(btn, callback) {
		if (list_view.loading) {
			return;
		}

		let args = list_view.get_query_args();
		args["limit_start"] = list_view.next_start;

		list_view.set_is_loading(true, btn);

		return $.ajax({
			url: "/api/method/frappe.www.list.get",
			data: args,
			statusCode: {
				200: function(r) {
					list_view.next_start = r.message.next_start;

					list_view.append_list(r.message.result);
					list_view.toggle_show_more_button(r.message.show_more);

					list_view.trigger_on_load_more(r);
					callback && callback(r);
				}
			}
		}).always(function() {
			list_view.set_is_loading(false, btn);
		});
	},

	get_query_args: function() {
		let args = frappe.utils.get_query_params();

		Object.assign(args, {
			doctype: "{{ doctype }}",
			pathname: location.pathname,
			web_form_name: frappe.web_form_name,
		});

		return args;
	},

	clear_list: function() {
		list_view.result_wrapper.empty();
	},

	append_list: function(rows) {
		$.each(rows || [], function(i, d) {
			list_view.append_row(d)
		});
	},

	append_row: function(row_html) {
		if (row_html) {
			$(row_html).appendTo(list_view.result_wrapper);
		}
	},

	toggle_show_more_button: function(show) {
		$(".website-list .more-block").toggleClass("hide", !show);
	},

	set_is_loading: function(is_loading, btn) {
		list_view.loading = Boolean(is_loading);
		if (btn) {
			$(btn).prop("disabled", list_view.loading);
		}
	},

	toggle_empty_result: function(is_empty) {
		$(".empty-apps-state").toggleClass("hide", !is_empty);
		$(".website-list").toggleClass("hide", !!is_empty);
	}
});

frappe.ready(function() {
	list_view.result_wrapper = $(".website-list .result");
	list_view.bind_events();
});

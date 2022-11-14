// website_script.js
{% if javascript -%}{{ javascript }}{%- endif %}

{% if enable_view_tracking %}
	if (navigator.doNotTrack != 1 && !window.is_404) {
		frappe.ready(() => {
			let browser = frappe.utils.get_browser();
			frappe.call("frappe.website.doctype.web_page_view.web_page_view.make_view_log", {
				path: location.pathname,
				referrer: document.referrer,
				browser: browser.name,
				version: browser.version,
				url: location.origin,
				user_tz: Intl.DateTimeFormat().resolvedOptions().timeZone
			})
		})
	}
{% endif %}

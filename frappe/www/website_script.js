// website_script.js
{% if javascript -%}{{ javascript }}{%- endif %}

{% if enable_view_tracking %}
	if (navigator.doNotTrack != 1 && !window.is_404) {
		frappe.ready(() => {
			let browser = frappe.utils.get_browser();
			let query_params = frappe.utils.get_query_params();

			// Get visitor ID based on browser uniqueness
			import('https://openfpcdn.io/fingerprintjs/v3')
				.then(fingerprint_js => fingerprint_js.load())
				.then(fp => fp.get())
				.then(result => {
					frappe.call("frappe.website.doctype.web_page_view.web_page_view.make_view_log", {
						referrer: document.referrer,
						browser: browser.name,
						version: browser.version,
						user_tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
						source: query_params.source,
						medium: query_params.medium,
						campaign: query_params.campaign,
						visitor_id: result.visitorId
					})
			})
		})
	}
{% endif %}

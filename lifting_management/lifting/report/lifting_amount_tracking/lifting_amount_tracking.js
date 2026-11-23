frappe.query_reports["Lifting Amount Tracking"] = {
	tree: true,
	name_field: "payment_wallet",
	parent_field: "parent_wallet",
	initial_depth: 0,
	filters: [
		{
			fieldname: "start_date",
			label: __("Start Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "end_date",
			label: __("End Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "truckon",
			label: __("Truckon"),
			fieldtype: "Link",
			options: "Truckon",
		},
		{
			fieldname: "payment_wallet",
			label: __("Payment Wallet"),
			fieldtype: "Link",
			options: "Payment Wallet",
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "dispatch_type",
			label: __("Dispatch Type"),
			fieldtype: "Select",
			options: "\nDDP\nEXW",
		},
		{
			fieldname: "location_from",
			label: __("Location From"),
			fieldtype: "Link",
			options: "Locations",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nScheduled\nClosed",
		},
		{
			fieldname: "request_order",
			label: __("Request Order"),
			fieldtype: "Data",
		},
	],
};

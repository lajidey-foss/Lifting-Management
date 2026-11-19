frappe.query_reports["Item Dispatch"] = {
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
			fieldname: "dispatch_type",
			label: __("Dispatch Type"),
			fieldtype: "Select",
			options: "\nDDP\nEXW",
		},
		{
			fieldname: "show_amount",
			label: __("Show Amount"),
			fieldtype: "Check",
		},
	],
};

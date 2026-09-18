// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.listview_settings["Truckon"] = {
	get_indicator: function (doc) {
		var status_color = {
			Draft: "red",
			Scheduled: "orange",
			Closed: "green",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};

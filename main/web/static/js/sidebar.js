import {dataSidebarMenu} from "../../data/dataSidebarMenu";
import {totalData} from "../data/totalData";

export const sidebarMenu = {
	view: "sidebar",
	css: "webix_dark sidebarMenu",
	select: true,
	scroll: true,
	data: dataSidebarMenu,
	ready() {
		const id = this.getFirstId();
		this.select(id);
	}
};

export const totalInfo = {
	view: "dataview",
	xCount: 3,
	yCount: 1,
	minWidth: 570,
	type: {
		height: 108,
		width: "auto",
		css: "totalItem"
	},
	template(obj) {
		const html = `
				<div class='flex'>
					<div class='totalCell flex'>
						<span class='totalTitle'>${obj.title}</span>
						<div class='totalCellSum flex'>
							<span class='thick totalSum'>${obj.total}</span>
							<span class='status ${obj.color}'>${obj.changes} <span class = '${obj.arrow}'></span> </span>
						</div>
						<span class='totalType'>${obj.type}</span>
					</div>
				</div>
							`;
		return html;
	},
	data: totalData
};
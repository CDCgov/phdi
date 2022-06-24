// Functionality for generating and maintaining the list of resources that are shown

function generate_resources() {
    let resource_lists = document.getElementsByClassName("resource-list");
    for (let i = 0; i < resource_lists.length; i++) {
        let list_id = resource_lists[i].id;
        let fields = CATEGORY_MAP[list_id];
        fields.sort();
        for (let j = 0; j < fields.length; j++) {
            let list_item = document.createElement("li");
            list_item.classList.add("resource");
            list_item.title = fields[j];

            let list_link = document.createElement("a");
            list_link.classList.add("resource-link");
            list_link.href = "#";
            list_link.title = fields[j];
            list_link.innerText = fields[j];

            list_item.appendChild(list_link);
            resource_lists[i].appendChild(list_item);
        }
    }
}

function remove_all_highlights() {
    const resources = document.getElementsByClassName("resource");
    for (let i = 0; i < resources.length; i++) {
        resources[i].classList.remove("active");
    }
}
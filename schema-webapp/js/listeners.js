// Functionality that needs to be bound to dynamically generated DOM elements lives here.

document.addEventListener("click", function (event) {
    // when a delete button is pressed, we want to remove the appropriate table, which
    // requires knowing which button called the function. However, the delete buttons are
    // dynamically added to the DOM, so we have to listen at the document level and drill
    // down from there.
    if (event.target.classList.contains("delete-icon")) {
        confirm_deletion(event.target.id);
    }

    // if a user attempts to edit an existing table, we should first make sure there are
    // not unsaved changes that have been made
    if (event.target.classList.contains("edit-icon")) {
        //confirm_edit(event.target.id);
        show_modal("notImplementedModal");
    }

    // when a resource is clicked, we want to display all of the fields available
    // in that resource, as well as highlight which resource the user is currently viewing
    if (event.target.classList.contains("resource-link")) {
        let resource = event.target.title;
        let _id = generate_id_from_string(resource, "table");

        hide_all_tables();
        show_table(_id);
        remove_all_highlights();
        event.target.parentNode.classList.add("active");
    }
})

// When a user is entering the name of a new table, they should be able to hit enter
// to accept the new name
document.addEventListener("DOMContentLoaded", function () {
    const name_input = document.getElementById("table-name");
    name_input.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            document.getElementById("table-name-submit").click();
        }
    })

    generate_resources();
    generate_all_field_tables();
})

// when the table name modal is shown, the input box should automatically be focused
document.addEventListener("shown.bs.modal", function () {
    const name_input = document.getElementById("table-name");
    name_input.focus();
})
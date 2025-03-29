from rolesOpste import kvartaliGodisnji, rolesOpsteDict
from rolesHR import rolesHRDict
from rolesProjekti import rolesProjektiDict
from dropDownFunctions import numbers_list_string_list, get_roles, get_previous_selection, get_combo_items, clear_all_dropdowns_below, get_points_for_activity
def update_dropdown(window, current_index, next_index, data_dict, type):
    
    # Get the current dropdown selection
    selected_value = get_previous_selection(window, current_index, type)
    
    # Get reference to the next dropdown
    if type == 'o':
        next_dropdown = getattr(window, f"dropDownOpste{next_index}", None)
    if type == 'h':
        next_dropdown = getattr(window, f"dropDownHR{next_index}", None)
    if type == 'p':
        next_dropdown = getattr(window, f"dropDownProjekti{next_index}", None)

    if not selected_value:
        clear_all_dropdowns_below(window, current_index, type)
        return

    next_dropdown.clear()  # Clear previous items

    if next_index == 3:
        if type == 'o':
            options = numbers_list_string_list(window, kvartaliGodisnji)
        if type == 'h':
            options = get_points_for_activity(window=window, type = type)
        if type == 'p':
            options = get_points_for_activity(window=window, type = type)
    elif next_index == 4:
        options = numbers_list_string_list(window,
            rolesOpsteDict[window.dropDownOpste1.currentText()].get(window.dropDownOpste2.currentText(), [])
        )
    else:
        options = list(data_dict.get(selected_value, {}).keys())

    if options:
        next_dropdown.addItem("")
        next_dropdown.addItems(options)
        next_dropdown.setEnabled(True)
    else:
        next_dropdown.setEnabled(False)
        next_dropdown.addItem("")  # Prevents issues with empty dropdowns
# convert [1,2,3] to ['1', '2', '3']
from rolesOpste import rolesOpsteDict
from rolesHR import rolesHRDict
from rolesProjekti import rolesProjektiDict
def numbers_list_string_list(self, numbers_list):
    return [str(number) for number in numbers_list]

# get keys list from the map
def get_roles(self, map):
    roles = []
    for key in map:
        roles.append(key)
    return roles

# get selection from the previous dropDown
def get_previous_selection(self, num, type):
    if type == 'o':
        dropdown = getattr(self, f"dropDownOpste{num}", None)
        return dropdown.currentText() if dropdown else None
    if type == 'h':
        dropdown = getattr(self, f"dropDownHR{num}", None)
        return dropdown.currentText() if dropdown else None
    if type == 'p':
        dropdown = getattr(self, f"dropDownProjekti{num}", None)
        return dropdown.currentText() if dropdown else None
    
# get all items currently available in dropDown
def get_combo_items(self, comboBox):
    return [comboBox.itemText(i) for i in range(comboBox.count())]


# when selection in one dropDown is blank, all dropDowns below are set to blank
def clear_all_dropdowns_below(self, next_index, type):
    for i in range(next_index + 1, 5):
        if type == 'o':
            dropdown = getattr(self, f"dropDownOpste{i}", None)
        if type == 'h':
            dropdown = getattr(self, f"dropDownHR{i}", None)
        if type == 'p':
            dropdown = getattr(self, f"dropDownProjekti{i}", None)
        if dropdown:
            dropdown.clear()
            dropdown.setEnabled(False)

def get_points_for_activity(window, type):
    if type == 'o':
        return numbers_list_string_list(window,
            rolesOpsteDict[window.dropDownOpste1.currentText()]
            .get(window.dropDownOpste2.currentText(), []))
    if type == 'h':
        return numbers_list_string_list(window,
            rolesHRDict[window.dropDownHR1.currentText()]
            .get(window.dropDownHR2.currentText(), []))
    if type == 'p':
        return numbers_list_string_list(window,
            rolesProjektiDict[window.dropDownProjekti1.currentText()]
            .get(window.dropDownProjekti2.currentText(), []))
    
def clear_all_dropdowns(self, next_index = 0):
    types = ['o', 'h', 'p']
    for type in types:
        for i in range(next_index + 1, 5):
            if type == 'o':
                dropdown = getattr(self, f"dropDownOpste{i}", None)
            if type == 'h':
                dropdown = getattr(self, f"dropDownHR{i}", None)
            if type == 'p':
                dropdown = getattr(self, f"dropDownProjekti{i}", None)
            if dropdown:
                dropdown.clear()
                dropdown.setEnabled(False)
    self.dropDownHR1.setEnabled(True)
    self.dropDownOpste1.setEnabled(True)
    self.dropDownProjekti1.setEnabled(True)
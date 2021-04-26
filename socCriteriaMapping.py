


import csv
import collections


# Takes the control_export as input and returns a dictionary of dictionaries
# where each dictionary is a framework in tbl. These are then dictionaries with
# their associated controls as keys mapping to empty lists
# control_export must be in csv form
def create_dict_of_frameworks(filename):
    framework_dicts = {}
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            next(reader, None) # This is to skip the header
            for row in reader:
                if row[6]: # col 6 has the frameworks, this checks it is not an empty cell
                    frameworks_list = row[6].split('\n')
                    for f in frameworks_list:
                        if f in framework_dicts:
                            framework = framework_dicts[f]
                            framework[row[1]] = [] # col 1 has the control name
                        else:
                            framework = {}
                            framework['label'] = f # Add the framework name to the dict
                            framework['codes'] = row[9].split('\n') # All the
                            framework[row[1]] = [] # Add control to framework
                            framework_dicts[f] =  framework # add framework to the framework dict

        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))
    return framework_dicts


# takes a dictionary of dictionaries, each representing a framework in tbl
# needs et_export in csv form
# maps ET ids to controls in each dict using et_export file
def fill_frameworks_with_ets(filename, framework_dicts):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            next(reader, None) # This is to skip the header
            for row in reader:
                framework_list = row[8].split('\n') # col 8 has the frameworks this et is used in
                for f in framework_list: # for each assocaited framework
                    if f in framework_dicts:
                        framework = framework_dicts[f]
                        control_list = row[7].split('\n') # col 7 contains the associated controls to this et
                        for control in control_list: # for each associated control
                            if control in framework: # control is in this framework, find it and add the et to it
                            #     print("CONTROL IN FRAMEWORK")
                            # else:
                            #     print("NOT IN FRAMEWORK")
                                et_list = framework[control]
                                et_list.append(row[0]) # col 0 has the ET id
                    # else:
                    #     print("err: encountered a framework that was not found")
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))


# Finds SOC criterias from the tbl controls_export and adds associated controls to them
# A SOC control can be in multiple criterias
# export has to be in csv form
def get_soc_criterias(filename):
    criteria_dict = {}
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            next(reader, None) # This is to skip the header
            for row in reader:
                associated_frameworks = row[6].split('\n')
                if "SOC 2" in associated_frameworks: # We only look at SOC 2 controls
                    criteria_list = row[9].split('\n') # All the soc Criterias are in row 9
                    # Add the criterias and fill them with associated controls
                    for c in criteria_list:
                        if not c.startswith("A.") and not c == "": # We don't want non-Soc 2 codes
                            if c in criteria_dict:
                                criteria = criteria_dict[c]
                                criteria[row[1]] = [] # col 1 has the control name
                            else:
                                criteria = {}
                                criteria['label'] = c # Give the criteria its name
                                criteria[row[1]] = [] # add the control to the criteria
                                criteria_dict[c] = criteria # add criteria to the dict

        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))
    return criteria_dict


# Using tbl evidenct task export, finds associated ets with the controls
# for each SOC 2 Criteria
def fill_soc_criterias(filename, criteria_dict):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            next(reader, None) # This is to skip the header
            for row in reader:
                framework_list = row[8].split('\n') # col 8 has the frameworks this et is used in
                if "SOC 2" in framework_list: # This et is used in SOC 2
                    associated_controls = row[7].split('\n')
                    for c in criteria_dict:
                        criteria = criteria_dict[c]
                        for control in associated_controls: # See which controls are part of each criteria
                            if control == "":
                                continue
                            if control in criteria:
                                # print("test")
                                et_list = criteria[control]
                                et_list.append(row[0]) # Add the ET id to the list
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))


# Returns a list of implemented ET ids given a list of framework dictionaries
def find_implemented_ETs(framework):
    ET_set = set()
    for control, control_ET_list in framework.iteritems():
        for ET_id in control_ET_list:
            ET_set.add(ET_id)
    return sorted(ET_set) # Returns a list of the ETs included in our frameworks


# Prints to the console the framework controls satisfied by each SOC criteria
def compare_criteria_framework_ets(soc_criteria_dict, framework):
    print(framework['label'])

    for c, criteria in sorted(soc_criteria_dict.iteritems()):
        print(criteria['label'])

        criteria_ets = find_implemented_ETs(criteria)

        for control, control_et_list in framework.iteritems():
            if control == 'label' or control == 'codes':
                continue # These aren't controls and dont want to look at them

            if all(et_id in criteria_ets for et_id in control_et_list):
                print(control)
        print('\n')


# creates a csv detailing the controls satisfied by each SOC criteria
def create_csv_mapping(soc_criteria_dict, framework):
    f_name = framework["label"]
    with open("SOC 2 _" +f_name + "mapping.csv", "w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["SOC Criteria", "SOC controls", f_name+" controls"])

                for c, criteria in sorted(soc_criteria_dict.iteritems()):
                    criteria_controls = criteria.keys()
                    f_controls = []

                    criteria_ets = find_implemented_ETs(criteria)
                    for control, control_et_list in framework.iteritems():
                        if control == 'label' or control == 'codes':
                            continue # These aren't controls and dont want to look at them

                        if all(et_id in criteria_ets for et_id in control_et_list):
                            f_controls.append(control)

                    writer.writerow([c, list_to_text(criteria_controls), list_to_text(f_controls)])


# Helps to format a list as a string
def list_to_text(list):
    text = ""
    for control in list:
        text = text + control + "\n"
    return text


def main():
        framework_dicts = create_dict_of_frameworks('controls_export.csv')
        fill_frameworks_with_ets('TugbotLogic-Evidence-Tasks.csv', framework_dicts)
        soc_criteria_dict = get_soc_criterias('controls_export.csv')
        fill_soc_criterias('TugbotLogic-Evidence-Tasks.csv', soc_criteria_dict)

        compare_criteria_framework_ets(soc_criteria_dict, framework_dicts['ISO 27001:2013'])
        create_csv_mapping(soc_criteria_dict, framework_dicts['ISO 27001:2013'])

if __name__ == "__main__":
    main()

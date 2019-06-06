import pandas as pd
from fedelemflowlist.globals import inputpath, as_path, log,flow_list_specs

contexts = pd.read_csv(inputpath + 'Contexts.csv', na_values='N/A') #
contexts.head(50)

#Get levels for max number of compartment classes
max_compartment_classes = len(contexts.columns)
compartment_levels = ['c_' + str(c) for c in range(0, max_compartment_classes)]

compartment_classes = flow_list_specs['primary_context_classes'] + flow_list_specs['secondary_context_classes']

if (compartment_classes != list(contexts.columns)):
    log.debug('ERROR: Compartment class list does not match column headers in Contexts sheet')



#Create dictionary of context levels
context_levels = {}
counter = 0
for c in compartment_classes:
    context_levels['c_' + str(counter)]=c
    counter=counter+1


#Drop duplicates just as a check
contexts = contexts.drop_duplicates()



#Describe a pattern of compartment classes used in each context
context_patterns = []
for index,row in contexts.iterrows():
    pattern = [compartment_classes[x] for x in range(0, max_compartment_classes) if str(row[x]) != 'nan']
    pattern = ','.join(pattern)
    context_patterns.append(pattern)


#Create a clean list with no NAs
context_list_na_removed = list()
for index,row in contexts.iterrows():
    row_list = row.values
    row_list_na_removed = [x for x in row.values if str(x) != 'nan']
    context_list_na_removed.append(row_list_na_removed)

#Used this clean list with no NAs, generate UUIDs
from fedelemflowlist.uuid_generators import generate_context_uuid
context_uuids = list()
context_paths = list()
for r in context_list_na_removed:
    #Pass the uuid function the list as a series of string arguments
    compartment_path = as_path(*r)
    context_paths.append(compartment_path)
    compartment_uuid = generate_context_uuid(*r)
    context_uuids.append(compartment_uuid)

d = {'Context':context_paths,'Context UUID':context_uuids,'Pattern':context_patterns}
context_path_uuid = pd.DataFrame(data=d)



# rows_as_list_with_nans = context_list_na_removed
#
# #Add NAs now to end to make lists equal length
# for r in rows_as_list_with_nans:
#     for i in range(0, max_compartment_classes - len(r)):
#         r.append(None)
#
# compartments = pd.DataFrame(rows_as_list_with_nans,columns=compartment_levels)
#
# compartments = compartments.sort_values(by=compartment_levels)
#
# compartments.to_csv('work/contexts_16April.csv',index=False)
#
# #Are they unique
# len(compartments)
# len(compartments.drop_duplicates())


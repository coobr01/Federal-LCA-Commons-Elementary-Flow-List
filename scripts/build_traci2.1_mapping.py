"""
Builds the mapping file for TRACI2.1 using input flowable and context mappings,
and TRACI2.1 from the lcia_formatter
Requires lciafmt from lcia_formatter (https://github.com/USEPA/lciaformatter)
BEWARE this will replace the existing mapping file if it exists in /flowmapping
"""

import pandas as pd
import fedelemflowlist
from fedelemflowlist.globals import inputpath, flowmappingpath

lcia_name = 'TRACI2.1'

if __name__ == '__main__':
    ## Bring in TRACI flowables and contexts from the lcia_formatter
    import lciafmt

    lcia_lciafmt = lciafmt.get_method('TRACI 2.1')
   
    
    """ due to substances listed more than once with different names
    this replaces all instances of the Original Flowable with a New Flowable
    based on a csv input file, otherwise zero values for CFs will override
    when there are duplicate names"""
    flowables_replace = pd.read_csv(inputpath+'/TRACI_2.1_replacement.csv')
    for index, row in flowables_replace.iterrows():
        orig = row['Original Flowable']
        new = row['New Flowable']
        lcia_lciafmt['Flowable']=lcia_lciafmt['Flowable'].replace(orig, new)    
    
    """ due to substances listed more than once with the same name but different CAS
    this replaces all instances of the Original Flowable with a New Flowable
    based on a csv input file according to the CAS"""
    flowables_split = pd.read_csv(inputpath+'/TRACI_2.1_split.csv')
    for index, row in flowables_split.iterrows():
        CAS = row['CAS']
        new = row['New Flowable']
        lcia_lciafmt.loc[lcia_lciafmt['CAS No'] == CAS, 'Flowable'] = new
        
    # Keep only flowable and category
    lcia_lciafmt = lcia_lciafmt[['Flowable', 'Context']]
    lcia_lciafmt = lcia_lciafmt.drop_duplicates()
    len(lcia_lciafmt)

    traci_lciafmt_contexts = pd.Series(pd.unique(lcia_lciafmt['Context']))


    # export and map these to Fed Commons flow list contexts
    # traci_lciafmt_contexts.to_csv('work/TRACI_lciafmt_contexts.csv',index=False)

    # Add in context matches. Assume these are in inputfolder with lcia_name+standardname.csv
    def get_manual_mappings(source, ftype):
        """
        Loads a csv mapping file
        :param source: source name
        :param ftype: 'Flowable' or 'Context'
        :return: mapping file
        """
        mappings = pd.read_csv(inputpath + source + ftype + 'Mappings.csv')
        return mappings


    context_mappings = get_manual_mappings(lcia_name, 'Context')
    lciafmt_w_context_mappings = pd.merge(lcia_lciafmt, context_mappings,
                                          left_on='Context',
                                          right_on='SourceFlowContext')
    # Drop duplicate field
    lciafmt_w_context_mappings = lciafmt_w_context_mappings.drop(columns=['Context'])
    len(lciafmt_w_context_mappings)

    # Add in flowable matches. Assume these are in inputfolder with lcia_name+standardname.csv
    flowable_mappings = pd.read_csv(inputpath + lcia_name + 'FlowableMappings.csv')
    len(flowable_mappings)
    lciafmt_w_context_flowable_mappings = pd.merge(lciafmt_w_context_mappings,
                                                   flowable_mappings,
                                                   left_on='Flowable',
                                                   right_on='SourceFlowName')
    # Drop duplicate field
    lciafmt_w_context_flowable_mappings = lciafmt_w_context_flowable_mappings.drop(columns='Flowable')
    len(lciafmt_w_context_flowable_mappings)

    # Merge LCIA with Flowlist
    # Load full flow list to get all the contexts
    flowlist = fedelemflowlist.get_flows()
    flowlist = flowlist[['Flowable', 'Context', 'Unit', 'Flow UUID', 'Preferred']]
    lcia_mappings = pd.merge(lciafmt_w_context_flowable_mappings, flowlist,
                             left_on=['TargetFlowName', 'TargetFlowContext', 'TargetUnit'],
                             right_on=['Flowable', 'Context', 'Unit'])

    # Clean up the mappings
    lcia_mappings = lcia_mappings.drop(columns=['Flowable', 'Context',
                                                'Unit', 'Note', 'Map method', 'Preferred'])
    lcia_mappings = lcia_mappings.rename(columns={'Flow UUID': 'TargetFlowUUID'})

    # Add LCIA name and missing fields
    lcia_mappings['SourceListName'] = lcia_name
    lcia_mappings['ConversionFactor'] = 1
    lcia_mappings['SourceFlowUUID'] = None
    len(lcia_mappings)

    # Reorder the mappings
    flowmapping_order = ['SourceListName',
                         'SourceFlowName',
                         'SourceFlowUUID',
                         'SourceFlowContext',
                         'SourceUnit',
                         'MatchCondition',
                         'ConversionFactor',
                         'TargetFlowName',
                         'TargetFlowUUID',
                         'TargetFlowContext',
                         'TargetUnit',
                         'Mapper',
                         'Verifier',
                         'LastUpdated']
    lcia_mappings = lcia_mappings[flowmapping_order]
    # Write them to a csv
    lcia_mappings.to_csv(flowmappingpath + lcia_name + '.csv', index=False)

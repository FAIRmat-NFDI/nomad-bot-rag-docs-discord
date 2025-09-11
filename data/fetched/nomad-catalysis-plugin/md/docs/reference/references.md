# References

!!! List of ELN Schemas from this Plugin
- Catalyst Sample
- Catalytic Reaction


!!! List of quantities and subsections in `Catalyst Sample`:
- name (string quantity)
- datetime (string quantity)
- lab_id (string quantity)
- description (rich text quantity)
- storing_institution (string quantity)
- catalyst_type (string quantity)
- form (string quantity)

- elemental_composition (SubSection, repeating):
    - element
    - atomic fraction
    - mass fraction

- components (SubSection, repeating):
    - component label
    - mass
    - mass fraction

- preparation_details (SubSection):
    - preparation_method(string quantity)
    - preparator
    - preparing institution

- surface (SubSection):
    - surface_area (float quantity)
    - method_surface_area_determination (string quantity)
    - dispersion (float quantity)


!!!List of quantities and subsections in `CatalyticReaction`:
- name
- starting_Time
- data_file
- ID
- reaction_type
- reaction_name
- experiment_handbook
- description
- location
- experimenter

- steps (SubSection, repeating):
    - name
    - start_time
    - comment

- samples (SubSection, repeating):
    - name
    - reference
    - lab_id

- instruments (SubSection,label: reactor setup, repeating):
    - name
    - reference
    - lab_id
    - reactor_type
    - bed_length
    - reactor_cross_section_area
    - reactor_diameter
    - reactor_volume

- reactor_filling (SubSection, repeating):
    - catalyst_name
    - sample_section_reference
    - catalyst_mass
    - catalyst_density
    - catalyst_volume
    - catalyst_sievefraction_upper_limit
    - catalyst_sievefraction_lower_limit
    - particle_size
    - diluent
    - diluent_sievefraction_upper_limit
    - diluent_sievefraction_lower_limit

- pretreatment (SubSection, repeating):
    *same as reaction conditions below*

- reaction_conditions (SubSection, repeating):
    - set_temperature
    - set_pressure
    - set_total_flow_rate
    - contact_time (label W|F)
    - sampling_frequency
    - time_on_stream
    - weight_hourly_space_velocity
    - gas_hourly_space_velocity
    - runs
    - subsection reagents:
        - name
        - gas_concentration_in
        - flow_rate
        - pure_component:
            - name
            - iupac_name...

- results (SubSection, repeating):
    - name
    - temperature
    - pressure
    - total_flow_rate
    - runs
    - time_on_stream
    - c_balance
    - reactants_conversions:
        - name
        - gas_concentration_in
        - gas_concentration_out
        - flow_rate
        - reference
        - conversion
        - conversion_type
        - conversion_product_based
        - conversion_reactant_based
        - pure_component:
            - name
            - iupac_name, ...
    - rates:
        - name
        - reaction_rate
        - specific_mass_rate
        - specific_surface_area_rate
        - rate
        - turn_over_frequency
    - products:
        - name
        - gas_concentration_in
        - flow_rate
        - gas_concentration_out
        - selectivity
        - product_yield
        - space_time_yield
        - pure_component:
            - name
            - iupac_name

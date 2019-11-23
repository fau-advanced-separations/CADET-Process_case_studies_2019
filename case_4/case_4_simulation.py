#!/usr/bin/env python3

from CADETProcess.processModel import Langmuir
from CADETProcess.processModel import Source, Column, Sink
from CADETProcess.processModel import FlowSheet
from CADETProcess.processModel import Process

process_name = flow_sheet_name = 'serial_ternary'
case_dir = 'case_4b'

# Binding Model
binding_model = Langmuir(n_comp=3, name='langmuir')
binding_model.adsorption_rate = [0.01, 0.015, 0.03]
binding_model.desorption_rate = [1, 1, 1]
binding_model.saturation_capacity = [100, 100, 200]

# Unit Operations
feed = Source(n_comp=3, name='feed')
feed.c = [10, 10, 10]

eluent_1 = Source(n_comp=3, name='eluent_1')
eluent_1.c = [0, 0, 0]

eluent_2 = Source(n_comp=3, name='eluent_2')
eluent_2.c = [0, 0, 0]

column_1 = Column(n_comp=3, name='column_1')
column_1.length = 0.3
column_1.diameter = 0.024
column_1.axial_dispersion = 4.7e-7
column_1.total_porosity = 0.7

column_1.binding_model = binding_model

column_2 = Column(n_comp=3, name='column_2')
column_2.length = 0.3
column_2.diameter = 0.024
column_2.axial_dispersion = 4.7e-7
column_2.total_porosity = 0.7

column_2.binding_model = binding_model

outlet_1 = Sink(n_comp=3, name='outlet_1')
outlet_2 = Sink(n_comp=3, name='outlet_2')

# flow sheet
fs = FlowSheet(n_comp=3, name=flow_sheet_name)

fs.add_unit(feed, feed_source=True)
fs.add_unit(eluent_1, eluent_source=True)
fs.add_unit(eluent_2, eluent_source=True)
fs.add_unit(column_1)
fs.add_unit(column_2)
fs.add_unit(outlet_1, chromatogram_sink=True)
fs.add_unit(outlet_2, chromatogram_sink=True)

fs.add_connection(feed, column_1)
fs.add_connection(eluent_1, column_1)
fs.add_connection(column_1, outlet_1)
fs.add_connection(column_1, column_2)
fs.add_connection(eluent_2, column_2)
fs.add_connection(column_2, outlet_2)

# Process
serial_ternary = Process(fs, name=process_name)

Q = 60/(60*1e6)

# Create Events and Durations
serial_ternary.add_event('feed_on', 'flow_sheet.feed.flow_rate', Q)
serial_ternary.add_event('feed_off', 'flow_sheet.feed.flow_rate', 0.0)
serial_ternary.add_duration('feed_duration', 'feed_on', 'feed_off')

serial_ternary.add_event('eluent_1_on', 'flow_sheet.eluent_1.flow_rate', Q)
serial_ternary.add_event('eluent_1_off', 'flow_sheet.eluent_1.flow_rate', 0.0)

serial_ternary.add_event_dependency('eluent_1_on', ['feed_off'], [1])
serial_ternary.add_event_dependency('eluent_1_off', ['feed_on'], [1])
serial_ternary.add_event_dependency('feed_off', ['feed_on', 'feed_duration'],[1,1])

serial_ternary.add_event('serial_on', 'flow_sheet.column_1.output_state', 1)
serial_ternary.add_event('serial_off', 'flow_sheet.column_1.output_state', 0)

serial_ternary.add_event('eluent_2_on', 'flow_sheet.eluent_2.flow_rate', Q)
serial_ternary.add_event('eluent_2_off', 'flow_sheet.eluent_2.flow_rate', 0.0)

serial_ternary.add_event_dependency('eluent_2_on', ['serial_off'], [1])
serial_ternary.add_event_dependency('eluent_2_off', ['serial_on'], [1])

# Set process times
serial_ternary.cycle_time = 222.5
serial_ternary.feed_duration.time = 30.8
serial_ternary.serial_off.time = 310.5
serial_ternary.serial_on.time = 310.7


if __name__ == '__main__':
    from CADETProcess.simulation import Cadet
    process_simulator = Cadet()
    process_simulator.evaluate_stationarity = True

    serial_ternary_sim_results = process_simulator.simulate(serial_ternary)
    serial_ternary_sim_results.save(case_dir)

    from CADETProcess.fractionation import optimize_fractionation
    serial_ternary_frac = optimize_fractionation(
            serial_ternary_sim_results.chromatograms,
            serial_ternary.process_meta,
            purity_required=0.95)
    serial_ternary_frac.save(case_dir)

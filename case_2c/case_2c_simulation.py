#!/usr/bin/env python3

from CADETProcess.processModel import Langmuir
from CADETProcess.processModel import Source, Column, Sink
from CADETProcess.processModel import FlowSheet
from CADETProcess.processModel import Process

process_name = flow_sheet_name = 'batch_long_ternary'
case_dir = 'case_2c'

# Binding Model
binding_model = Langmuir(n_comp=3, name='langmuir')
binding_model.adsorption_rate = [0.01, 0.015, 0.03]
binding_model.desorption_rate = [1, 1, 1]
binding_model.saturation_capacity = [100, 100, 200]

# Unit Operations
feed = Source(n_comp=3, name='feed')
feed.c = [10, 10, 10]

eluent = Source(n_comp=3, name='eluent')
eluent.c = [0, 0, 0]

column = Column(n_comp=3, name='column')
column.length = 0.376
column.diameter = 0.024
column.axial_dispersion = 4.7e-7
column.total_porosity = 0.7

column.binding_model = binding_model

outlet = Sink(n_comp=3, name='outlet')

# flow sheet
fs = FlowSheet(n_comp=3, name=flow_sheet_name)

fs.add_unit(feed, feed_source=True)
fs.add_unit(eluent, eluent_source=True)
fs.add_unit(column)
fs.add_unit(outlet, chromatogram_sink=True)

fs.add_connection(feed, column)
fs.add_connection(eluent, column)
fs.add_connection(column, outlet)

# Process
batch_long_ternary = Process(fs, name=process_name)

Q = 60/(60*1e6)

# Create Events and Durations
batch_long_ternary.add_event('feed_on', 'flow_sheet.feed.flow_rate', Q)
batch_long_ternary.add_event('feed_off', 'flow_sheet.feed.flow_rate', 0.0)
batch_long_ternary.add_duration('feed_duration', 'feed_on', 'feed_off')

batch_long_ternary.add_event('eluent_on', 'flow_sheet.eluent.flow_rate', Q)
batch_long_ternary.add_event('eluent_off', 'flow_sheet.eluent.flow_rate', 0.0)

batch_long_ternary.add_event_dependency('eluent_on', ['feed_off'])
batch_long_ternary.add_event_dependency('eluent_off', ['feed_on'])
batch_long_ternary.add_event_dependency('feed_off', ['feed_on', 'feed_duration'], [1,1])

batch_long_ternary.cycle_time = 135.134
batch_long_ternary.feed_duration.time = 16.268


if __name__ == '__main__':
    from CADETProcess.simulation import Cadet
    process_simulator = Cadet()
    process_simulator.evaluate_stationarity = True

    batch_long_ternary_sim_results = process_simulator.simulate(batch_long_ternary)
    batch_long_ternary_sim_results.save(case_dir)

    from CADETProcess.fractionation import optimize_fractionation
    batch_long_ternary_frac = optimize_fractionation(
            batch_long_ternary_sim_results.chromatograms,
            batch_long_ternary.process_meta,
            purity_required=[0, 0.95, 0])
    batch_long_ternary_frac.save(case_dir)

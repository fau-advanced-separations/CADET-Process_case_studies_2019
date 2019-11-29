#!/usr/bin/env python3

from CADETProcess.processModel import Langmuir
from CADETProcess.processModel import Source, Column, Cstr, Sink
from CADETProcess.processModel import FlowSheet
from CADETProcess.processModel import Process

process_name = flow_sheet_name = 'ssr_binary'
case_dir = 'case_3a'

# Binding Model
binding_model = Langmuir(n_comp=2, name='langmuir')
binding_model.adsorption_rate = [0.02, 0.03]
binding_model.desorption_rate = [1, 1]
binding_model.saturation_capacity = [100, 100]

# Unit Operations
feed = Source(n_comp=2, name='feed')
feed.c = [10, 10]

eluent = Source(n_comp=2, name='eluent')
eluent.c = [0, 0]

tank = Cstr(n_comp=2, name='tank')
tank.V = 0.001
tank.c = [10, 10]

column = Column(n_comp=2, name='column')
column.length = 0.6
column.diameter = 0.024
column.axial_dispersion = 2.4e-6
column.total_porosity = 0.7

column.binding_model = binding_model

outlet = Sink(n_comp=2, name='outlet')

# flow sheet
fs = FlowSheet(n_comp=2, name=flow_sheet_name)

fs.add_unit(feed, feed_source=True)
fs.add_unit(eluent, eluent_source=True)
fs.add_unit(tank)
fs.add_unit(column)
fs.add_unit(outlet, chromatogram_sink=True)

fs.add_connection(feed, tank)
fs.add_connection(tank, column)
fs.add_connection(eluent, column)
fs.add_connection(column, tank)
fs.add_connection(column, outlet)

# Process
ssr_binary = Process(fs, name=process_name)

Q = 60/(60*1e6)
# Create Events and Durations
ssr_binary.add_event('feed_on', 'flow_sheet.feed.flow_rate', Q)
ssr_binary.add_event('feed_off', 'flow_sheet.feed.flow_rate', 0.0)
ssr_binary.add_duration('feed_duration', 'feed_on', 'feed_off')

ssr_binary.add_event('inject_on', 'flow_sheet.tank.flow_rate', Q)
ssr_binary.add_event('inject_off', 'flow_sheet.tank.flow_rate', 0.0)

ssr_binary.add_event('eluent_on', 'flow_sheet.eluent.flow_rate', Q)
ssr_binary.add_event_dependency('eluent_on', ['inject_off'])
ssr_binary.add_event('eluent_off', 'flow_sheet.eluent.flow_rate', 0.0)
ssr_binary.add_event_dependency('eluent_off', ['inject_on'])

ssr_binary.add_event('recycle_on', 'flow_sheet.column.output_state', 0)
ssr_binary.add_event('recycle_off', 'flow_sheet.column.output_state', 1)

ssr_binary.add_event_dependency('feed_on', ['inject_off'])
ssr_binary.add_event_dependency('feed_off', ['feed_on', 'feed_duration'], [1,1])
ssr_binary.add_event_dependency(
        'inject_off', ['inject_on', 'feed_duration', 'recycle_off', 'recycle_on'],
        [1,1,1,-1])

# Set process times
ssr_binary.cycle_time = 191.11
ssr_binary.feed_duration.time = 42.956
ssr_binary.recycle_on.time = 354.081
ssr_binary.recycle_off.time = 358.552


if __name__ == '__main__':
    from CADETProcess.simulation import Cadet
    process_simulator = Cadet()
    process_simulator.evaluate_stationarity = True
    process_simulator.n_cycles_min = 4
    ssr_binary_sim_results = process_simulator.simulate(ssr_binary)
    ssr_binary_sim_results.save(case_dir)

    from CADETProcess.fractionation import optimize_fractionation
    ssr_binary_frac = optimize_fractionation(
            ssr_binary_sim_results.chromatograms,
            ssr_binary.process_meta,
            purity_required=0.95)
    ssr_binary_frac.save(case_dir)

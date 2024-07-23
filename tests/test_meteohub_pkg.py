from meteohub import run_meteohub

# meteohub.main(dataset='dataset', date='date', run='run', start_fc='start_fc', end_fc='end_fc', out='out', fc_range='fc_range', varname='varname', bbox='bbox', t_srs='t_srs', version=False, debug=False, verbose=False)

result = run_meteohub(dataset="COSMO-2I",varname="tp",bbox="11.9,45,13.2,46", date="2024-07-19", run="00:00", out="rain_25_26.tif", start_fc=25, end_fc=26, debug=True)

print(result)
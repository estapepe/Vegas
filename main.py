import Vegas

replicate_cardinality = 10
alpha_experiment = Vegas.Experiment(10, Vegas.Experiment.ALPHA)
experiments = [alpha_experiment]

current_experiment_set = Vegas.ExperimentSet(experiments)
current_experiment_set.execute()

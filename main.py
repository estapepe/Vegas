import Vegas

replicate_cardinality = 100
alpha_experiment = Vegas.Experiment(replicate_cardinality, Vegas.Experiment.ALPHA)
beta_experiment = Vegas.Experiment(replicate_cardinality, Vegas.Experiment.BETA)
gamma_experiment = Vegas.Experiment(replicate_cardinality, Vegas.Experiment.GAMMA)
delta_experiment = Vegas.Experiment(replicate_cardinality, Vegas.Experiment.DELTA)
epsilon_experiment = Vegas.Experiment(replicate_cardinality, Vegas.Experiment.EPSILON)
zeta_experiment = Vegas.Experiment(replicate_cardinality, Vegas.Experiment.ZETA)
#experiments = [beta_experiment, gamma_experiment, delta_experiment, epsilon_experiment, zeta_experiment]
experiments = [alpha_experiment]

current_experiment_set = Vegas.ExperimentSet(experiments)
current_experiment_set.execute()

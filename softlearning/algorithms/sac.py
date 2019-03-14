from collections import OrderedDict

import numpy as np

from .rl_algorithm import RLAlgorithm
from .sac_agent import SACAgent

class SAC(RLAlgorithm):
    def __init__(
            self,
            variant,
            plotter=None,
            **kwargs):
        """
        Args:
            env (`SoftlearningEnv`): Environment used for training.
            policy: A policy function approximator.
            initial_exploration_policy: ('Policy'): A policy that we use
                for initial exploration which is not trained by the algorithm.
            Qs: Q-function approximators. The min of these
                approximators will be used. Usage of at least two Q-functions
                improves performance by reducing overestimation bias.
            pool (`PoolBase`): Replay pool to add gathered samples to.
            plotter (`QFPolicyPlotter`): Plotter instance to be used for
                visualizing Q-function during training.
            lr (`float`): Learning rate used for the function approximators.
            discount (`float`): Discount factor for Q-function updates.
            tau (`float`): Soft value function target update weight.
            target_update_interval ('int'): Frequency at which target network
                updates occur in iterations.
            reparameterize ('bool'): If True, we use a gradient estimator for
                the policy derived using the reparameterization trick. We use
                a likelihood ratio based estimator otherwise.
        """
        #print("sac kwargs", kwargs)
        super(SAC, self).__init__(**kwargs)

        self.agent = SACAgent(
            variant,
            **kwargs
        )
        self._plotter = plotter

    def _initial_exploration_hook(self):
        self.agent.initial_exploration()

    def _init_training(self):
        self.agent.init_training()

    def _init_sampler(self):
        self.agent.init_sampler()

    def _total_samples(self):
        return self.agent.total_samples()

    def _do_sampling(self, timestep):
        self.agent.do_sampling(timestep)

    def _terminate_sampler(self):
        self.agent.terminate_sampler()

    def train(self, *args, **kwargs):
        """Initiate training of the SAC instance."""

        return self._train(
            *args,
            **kwargs)

    def _do_training(self, iteration):
        self.agent.do_training(iteration)

    @property
    def ready_to_train(self):
        return self.agent.ready_to_train()

    def _training_batch(self, batch_size=None):
        return self.agent.training_batch(batch_size=batch_size)

    def _training_paths(self, epoch_length):
        return self.agent.training_paths(epoch_length)

    def _evaluation_paths(self):
        if self._eval_n_episodes < 1: return ()

        paths = self.agent.evaluation_paths(self._eval_n_episodes,
                                            self._eval_deterministic,
                                            self._eval_render_mode)

        return paths

    def _env_path_info(self, paths):
        return self.agent.env_path_info(paths)

    def _eval_env_path_info(self, paths):
        return self.agent.eval_env_path_info(paths)

    def _sampler_diagnostics(self):
        return self.agent.sampler_diagnostics()

    def get_diagnostics(self,
                        iteration,
                        batch,
                        training_paths,
                        evaluation_paths):
        """Return diagnostic information as ordered dictionary.

        Records mean and standard deviation of Q-function and state
        value function, and TD-loss (mean squared Bellman error)
        for the sample batch.

        Also calls the `draw` method of the plotter, if plotter defined.
        """

        Q_values, Q_losses, alpha, global_step = self.agent.get_diagnostics(iteration, batch)

        diagnostics = OrderedDict({
            'Q-avg': np.mean(Q_values),
            'Q-std': np.std(Q_values),
            'Q_loss': np.mean(Q_losses),
            'alpha': alpha,
        })

        policy_diagnostics = self.agent.policy_diagnostics(batch)
        diagnostics.update({
            f'policy/{key}': value
            for key, value in policy_diagnostics.items()
        })

        if self._plotter:
            self._plotter.draw()

        return diagnostics

    def _attempt_render(self, paths):
        self.agent.render_rollouts(paths)

import unittest

from common.simulator import Simulator, generate_scenario, run_agent
from players.adri.solution import decide as adri_decide
from players.raquel.solution import decide as raquel_decide


class SimulatorTests(unittest.TestCase):
    def test_scenario_is_deterministic(self):
        first = generate_scenario(42)
        second = generate_scenario(42)
        self.assertEqual(first, second)

    def test_targets_are_not_obstacles(self):
        scenario = generate_scenario(42)
        self.assertTrue(all(target not in scenario.obstacles for target in scenario.targets))
        self.assertNotIn(scenario.base, scenario.obstacles)

    def test_invalid_move_is_penalized(self):
        scenario = generate_scenario(5, size=5, obstacle_count=0, target_count=1)
        sim = Simulator(scenario)
        initial_energy = sim.energy
        sim.step("NOT_AN_ACTION")
        self.assertEqual(sim.invalid_moves, 1)
        self.assertEqual(sim.energy, initial_energy - 1)

    def test_both_starter_agents_can_run(self):
        scenario = generate_scenario(7)
        for decide in (adri_decide, raquel_decide):
            result = run_agent(decide, scenario)
            self.assertIsInstance(result["score"], int)
            self.assertGreaterEqual(result["visited"], 0)


if __name__ == "__main__":
    unittest.main()

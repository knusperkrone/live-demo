import random
from collections import namedtuple

from locust import FastHttpUser, LoadTestShape, between, task


class WebsiteUser(FastHttpUser):
    wait_time = between(2, 3)

    def on_start(self):
        self.wait()

    @task
    def index(self):
        n = random.choice([*range(10, 40)])
        self.client.get(f"/api/fib/{n}", timeout=(5, 65))


Step = namedtuple("Step", ["users", "ramp", "dwell"])


class StepLoadShape(LoadTestShape):
    targets_with_times = [
        Step(100, 5, 60 * 1),
        Step(300, 10, 60 * 1),
        Step(100, 5, 60 * 1),
        Step(1, 5, 60 * 5),
    ]

    def __init__(self, *args, **kwargs):
        self.step = 0
        self.time_active = False
        super(StepLoadShape, self).__init__(*args, **kwargs)

    def tick(self):
        if self.step >= len(self.targets_with_times):
            return None

        target = self.targets_with_times[self.step]
        users = self.get_current_user_count()

        if target.users == users:
            if not self.time_active:
                self.reset_time()
                self.time_active = True
            run_time = self.get_run_time()
            if run_time > target.dwell:
                self.step += 1
                self.time_active = False

        return (target.users, target.ramp)

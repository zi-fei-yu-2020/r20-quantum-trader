"""Local operations may pause scheduled entries without disabling protection."""
import os
import unittest
from unittest.mock import patch
from r20_gateway import scheduler, supervisor


class LocalRuntimeControlsTests(unittest.TestCase):
    def test_explicit_no_autostart_does_not_spawn_worker(self):
        with patch.dict(os.environ, {"R20_GATEWAY_AUTOSTART": "0", "R20_TESTING": "0"}), \
             patch.object(supervisor.sys, "platform", "linux"), \
             patch.object(supervisor, "ensure_worker") as spawn:
            supervisor.start_supervisor()
            spawn.assert_not_called()

    def test_pause_excludes_trader_but_keeps_independent_protection(self):
        for flag in ("0", "false", "invalid", ""):
            with self.subTest(flag=flag), \
                 patch("scripts.okx_runtime._load_dotenv", return_value={"R20_AUTOTRADE_ENABLED": flag}), \
                 patch.object(scheduler, "backup_job_specs", return_value=()):
                names = {job.name for job in scheduler.current_jobs()}
                self.assertNotIn("trader", names)
                self.assertTrue({"position_guard", "ledger_sync", "evidence_sync"} <= names)

    def test_normal_deployment_default_keeps_trader(self):
        for config in ({}, {"R20_AUTOTRADE_ENABLED": "1"}):
            with patch("scripts.okx_runtime._load_dotenv", return_value=config), \
                 patch.object(scheduler, "backup_job_specs", return_value=()):
                self.assertIn("trader", {job.name for job in scheduler.current_jobs()})

    def test_pause_is_reloaded_without_restarting_worker(self):
        with patch("scripts.okx_runtime._load_dotenv", side_effect=[
                {"R20_AUTOTRADE_ENABLED": "1"}, {"R20_AUTOTRADE_ENABLED": "0"}]), \
             patch.object(scheduler, "backup_job_specs", return_value=()):
            self.assertIn("trader", {job.name for job in scheduler.current_jobs()})
            self.assertNotIn("trader", {job.name for job in scheduler.current_jobs()})

    def test_status_exposes_controls_without_secrets(self):
        with patch("scripts.okx_runtime._load_dotenv", return_value={
                "R20_GATEWAY_AUTOSTART":"1", "R20_AUTOTRADE_ENABLED":"0", "LLM_API_KEY":"DO-NOT-RETURN"}):
            self.assertEqual(scheduler.runtime_controls(), {"gateway_autostart":True,"automatic_trader":False})

import os
import shutil
from datetime import datetime

import pandas as pd
import pytest

from taipy.common.alias import CycleId, Dag, PipelineId, ScenarioId
from taipy.common.frequency import Frequency
from taipy.config import Config, GlobalAppConfig, JobConfig
from taipy.cycle.cycle import Cycle
from taipy.cycle.cycle_model import CycleModel
from taipy.cycle.manager import CycleManager
from taipy.data.manager import DataManager
from taipy.job import JobManager
from taipy.pipeline import Pipeline, PipelineManager
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.scenario import ScenarioManager
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel
from taipy.task.manager import TaskManager

current_time = datetime.now()


@pytest.fixture(scope="function")
def csv_file(tmpdir_factory) -> str:
    csv = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.csv")
    csv.to_csv(str(fn), index=False)
    return fn.strpath


@pytest.fixture(scope="function")
def excel_file(tmpdir_factory) -> str:
    excel = pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")
    excel.to_excel(str(fn), index=False)
    return fn.strpath


@pytest.fixture(scope="function")
def excel_file_with_multi_sheet(tmpdir_factory) -> str:
    excel_multi_sheet = {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }
    fn = tmpdir_factory.mktemp("data").join("df.xlsx")

    writer = pd.ExcelWriter(str(fn))
    for key in excel_multi_sheet.keys():
        excel_multi_sheet[key].to_excel(writer, key, index=False)
    writer.save()

    return fn.strpath


@pytest.fixture(scope="function")
def default_data_frame():
    return pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}])


@pytest.fixture(scope="function")
def default_multi_sheet_data_frame():
    return {
        "Sheet1": pd.DataFrame([{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]),
        "Sheet2": pd.DataFrame([{"a": 7, "b": 8, "c": 9}, {"a": 10, "b": 11, "c": 12}]),
    }


@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(".data"):
        shutil.rmtree(".data")


@pytest.fixture(scope="function")
def current_datetime():
    return current_time


@pytest.fixture(scope="function")
def scenario(cycle):
    return Scenario("sc", [], {}, ScenarioId("sc_id"), current_time, is_master=False, cycle=None)


@pytest.fixture(scope="function")
def scenario_model(cycle):
    return ScenarioModel(
        ScenarioId("sc_id"),
        "sc",
        [],
        {},
        creation_date=current_time.isoformat(),
        master_scenario=False,
        subscribers=[],
        cycle=None,
    )


@pytest.fixture(scope="function")
def cycle():
    example_date = datetime.fromisoformat("2021-11-11T11:11:01.000001")
    return Cycle(
        Frequency.DAILY,
        {},
        creation_date=example_date,
        start_date=example_date,
        end_date=example_date,
        name="cc",
        id=CycleId("cc_id"),
    )


@pytest.fixture(scope="class")
def pipeline():
    return Pipeline("pipeline", {}, [], PipelineId("pipeline_id"))


@pytest.fixture(scope="function")
def cycle_model():
    return CycleModel(
        CycleId("cc_id"),
        "cc",
        Frequency.DAILY,
        {},
        creation_date="2021-11-11T11:11:01.000001",
        start_date="2021-11-11T11:11:01.000001",
        end_date="2021-11-11T11:11:01.000001",
    )


@pytest.fixture(scope="class")
def pipeline_model():
    return PipelineModel(PipelineId("pipeline_id"), None, "pipeline", {}, Dag({}), Dag({}), [])


@pytest.fixture(scope="function", autouse=True)
def setup():
    delete_everything()


def delete_everything():
    TaskManager._scheduler = None
    ScenarioManager.delete_all()
    PipelineManager.delete_all()
    DataManager.delete_all()
    TaskManager.delete_all()
    JobManager.delete_all()
    CycleManager.delete_all()
    Config._python_config.global_config = GlobalAppConfig()
    Config._python_config.job_config = JobConfig()
    Config._python_config.data_nodes.clear()
    Config._python_config.tasks.clear()
    Config._python_config.pipelines.clear()
    Config._python_config.scenarios.clear()


@pytest.fixture(scope="function", autouse=True)
def teardown():
    delete_everything()

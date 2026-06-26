import pytest
from pawpal_system import Pet, Task


@pytest.fixture
def sample_task():
    return Task(task_id=1, pet_id=10, name="Walk", task_type="exercise", duration=30, priority=2)


@pytest.fixture
def sample_pet():
    return Pet(pet_id=10, name="Buddy", species="dog", age=3)


def test_mark_complete_changes_status(sample_task):
    assert sample_task.completed is False
    sample_task.mark_complete()
    assert sample_task.completed is True


def test_add_task_increases_pet_task_count(sample_pet, sample_task):
    assert len(sample_pet.tasks) == 0
    sample_pet.add_task(sample_task)
    assert len(sample_pet.tasks) == 1

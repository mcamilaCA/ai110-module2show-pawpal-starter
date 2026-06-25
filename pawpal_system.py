from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Owner:
    owner_id: int
    name: str
    available_time: int
    preferences: List[str] = field(default_factory=list)

    def update_available_time(self, time: int) -> None:
        self.available_time = time

    def add_preference(self, pref: str) -> None:
        self.preferences.append(pref)

    def remove_preference(self, pref: str) -> None:
        self.preferences.remove(pref)


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    age: int

    def update_age(self, age: int) -> None:
        self.age = age


@dataclass
class CareTask:
    task_id: int
    name: str
    task_type: str
    duration: int
    priority: int
    is_daily: bool = False
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True

    def mark_incomplete(self) -> None:
        self.completed = False

    def update_priority(self, priority: int) -> None:
        self.priority = priority


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self._owner: Owner = owner
        self._pet: Pet = pet
        self._tasks: List[CareTask] = []
        self._scheduled_tasks: List[CareTask] = []
        self._total_duration: int = 0
        self._explanation: List[str] = []

    def add_task(self, task: CareTask) -> None:
        self._tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        self._tasks = [t for t in self._tasks if t.task_id != task_id]
        self._scheduled_tasks = [t for t in self._scheduled_tasks if t.task_id != task_id]

    def edit_task(self, task_id: int, **kwargs) -> None:
        for task in self._tasks:
            if task.task_id == task_id:
                for attr, value in kwargs.items():
                    setattr(task, attr, value)
                return

    def rank_tasks(self) -> List[CareTask]:
        return sorted(self._tasks, key=lambda t: t.priority, reverse=True)

    def generate_plan(self) -> List[CareTask]:
        ranked = self.rank_tasks()
        self._scheduled_tasks = []
        accumulated = 0
        for task in ranked:
            if accumulated + task.duration <= self._owner.available_time:
                self._scheduled_tasks.append(task)
                accumulated += task.duration
        self._total_duration = accumulated
        return self._scheduled_tasks

    def calculate_total_duration(self) -> int:
        self._total_duration = sum(t.duration for t in self._scheduled_tasks)
        return self._total_duration

    def generate_explanation(self) -> List[str]:
        self._explanation = [
            f"Scheduled '{t.name}' (priority={t.priority}, duration={t.duration} min)"
            for t in self._scheduled_tasks
        ]
        return self._explanation

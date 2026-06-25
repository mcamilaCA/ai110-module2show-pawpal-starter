from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Owner:
    owner_id: int
    name: str
    available_time: int
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)
    
    def remove_pet(self, pet_id: int) -> None:
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def update_available_time(self, time: int) -> None:
        self.available_time = time

    def add_preference(self, pref: str) -> None:
        self.preferences.append(pref)

    def remove_preference(self, pref: str) -> None:
        if pref in self.preferences:
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
class Task:
    task_id: int
    name: str
    task_type: str
    duration: int
    priority: int
    is_daily: bool = False
    completed: bool = False
    pet_id: int  # pet associated with the task

    def mark_complete(self) -> None:
        self.completed = True

    def mark_incomplete(self) -> None:
        self.completed = False

    def update_priority(self, priority: int) -> None:
        self.priority = priority


class Scheduler:
    def __init__(self, owner: Owner, pets: List[Pet]) -> None:
        self._owner: Owner = owner
        self._pets: List[Pet] = pets
        self._tasks: List[Task] = []
        self._scheduled_tasks: List[Task] = []
        self._total_duration: int = 0
        self._explanation: List[str] = []

    def add_task(self, task: Task) -> None:
        pet_ids = {pet.pet_id for pet in self._pets}
        
        if task.pet_id is not None and task.pet_id not in pet_ids:
            raise ValueError(f'No pet with id {task.pet_id} is registered in this system.')
        
        self._tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        self._tasks = [t for t in self._tasks if t.task_id != task_id]
        self._scheduled_tasks = [t for t in self._scheduled_tasks if t.task_id != task_id]

    VALID_TASK_ATTRIBUTES = {'name', 'task_type', 'duration', 'priority', 'is_daily', 'completed', 'pet_id'}
    def edit_task(self, task_id: int, **kwargs) -> None:
        invalid = set(kwargs) - self.VALID_TASK_ATTRIBUTES
        
        if invalid:
            raise ValueError(f"Invalid task attributes: {invalid}")
        
        if "duration" in kwargs and kwargs["duration"] < 0:
            raise ValueError("Duration must be non-negative")
        
        for task in self._tasks:
            if task.task_id == task_id:
                for attr, value in kwargs.items():
                    setattr(task, attr, value)
                self._scheduled_tasks = [] 
                self._total_duration = 0
                return

    def rank_tasks(self) -> List[Task]:
        preferences = set(self._owner.preferences)

        def sort_key( t: Task):
            bonus = 1 if t.task_type in preferences else 0
            return (t.priority + bonus, t.duration)
        
        return sorted(self._tasks, key=sort_key, reverse=True)


    def generate_plan(self) -> List[Task]:
        ranked = self.rank_tasks()
        self._scheduled_tasks = []
        accumulated = 0
        for task in ranked:
            if task.completed and not task.is_daily:
                continue

            if accumulated + task.duration <= self._owner.available_time:
                self._scheduled_tasks.append(task)
                accumulated += task.duration
        self._total_duration = accumulated
        return self._scheduled_tasks

    def reset_daily_tasks(self) -> None:
        for task in self._tasks:
            if task.is_daily:
                task.completed = False

    def calculate_total_duration(self) -> int:
        self._total_duration = sum(t.duration for t in self._scheduled_tasks)
        return self._total_duration

    def generate_explanation(self) -> List[str]:
        self._explanation = [
            f"Scheduled '{t.name}' (priority={t.priority}, duration={t.duration} min)"
            for t in self._scheduled_tasks
        ]
        return self._explanation

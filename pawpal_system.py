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
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove the pet with the given ID from this owner's list."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def update_available_time(self, time: int) -> None:
        """Set the owner's available time in minutes."""
        self.available_time = time

    def add_preference(self, pref: str) -> None:
        """Append a task-type preference to this owner's preference list."""
        self.preferences.append(pref)

    def remove_preference(self, pref: str) -> None:
        """Remove a task-type preference if it exists."""
        if pref in self.preferences:
            self.preferences.remove(pref)


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def update_age(self, age: int) -> None:
        """Update the pet's age."""
        self.age = age

    def add_task(self, task: Task) -> None:
        """Add a task to this pet, raising ValueError if the task ID already exists."""
        if any(t.task_id == task.task_id for t in self.tasks):
            raise ValueError(f'Task with id {task.task_id} already exists for this pet.')
        task.pet_id = self.pet_id
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]


@dataclass
class Task:
    task_id: int
    pet_id: int  # pet associated with the task
    name: str
    task_type: str
    duration: int
    priority: int
    is_daily: bool = False
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def update_priority(self, priority: int) -> None:
        """Set a new priority value for this task."""
        self.priority = priority


class Scheduler:
    def __init__(self, owner: Owner, pets: List[Pet]) -> None:
        self._owner: Owner = owner
        self._pets: List[Pet] = pets
        self._scheduled_tasks: List[Task] = []
        self._explanation: List[str] = []

    @property
    def _tasks(self) -> List[Task]:
        """Return a flat list of all tasks across every registered pet."""
        return [task for pet in self._pets for task in pet.tasks]

    def add_task(self, task: Task) -> None:
        """Add a task to the appropriate pet, raising ValueError if the pet is not registered."""
        pet = next((p for p in self._pets if p.pet_id == task.pet_id), None)
        if pet is None:
            raise ValueError(f'No pet with id {task.pet_id} is registered in this system.')
        pet.add_task(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task by ID from all pets and from the current scheduled list."""
        for pet in self._pets:
            pet.remove_task(task_id)
        self._scheduled_tasks = [t for t in self._scheduled_tasks if t.task_id != task_id]

    VALID_TASK_ATTRIBUTES = {'name', 'task_type', 'duration', 'priority', 'is_daily', 'completed', 'pet_id'}
    def edit_task(self, task_id: int, **kwargs) -> None:
        """Update one or more attributes of a task, clearing the cached schedule on success."""
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
                self._explanation = []
                return

    def rank_tasks(self) -> List[Task]:
        """Return all tasks sorted by priority (boosted by owner preferences), daily status, and duration."""
        preferences = set(self._owner.preferences)

        def sort_key(t: Task):
            bonus = 1 if t.task_type in preferences else 0
            return (t.priority + bonus, t.is_daily, -t.duration)

        return sorted(self._tasks, key=sort_key, reverse=True)


    def generate_plan(self) -> List[Task]:
        """Build and return the highest-priority tasks that fit within the owner's available time."""
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

    def generate_plan_for_pet(self, pet_id: int) -> List[Task]:
        """Return a ranked, time-bounded task list for a single pet."""
        pet = next((p for p in self._pets if p.pet_id == pet_id), None)
        if pet is None:
            raise ValueError(f'No pet with id {pet_id} found.')

        preferences = set(self._owner.preferences)

        def sort_key(t: Task):
            bonus = 1 if t.task_type in preferences else 0
            return (t.priority + bonus, t.is_daily, -t.duration)

        ranked = sorted(pet.tasks, key=sort_key, reverse=True)
        scheduled, accumulated = [], 0
        for task in ranked:
            if task.completed and not task.is_daily:
                continue
            if accumulated + task.duration <= self._owner.available_time:
                scheduled.append(task)
                accumulated += task.duration
        return scheduled

    _SPECIES_EMOJI = {"dog": "🐶", "cat": "🐱", "bird": "🐦", "rabbit": "🐰", "fish": "🐟"}

    def _species_emoji(self, species: str) -> str:
        """Return the emoji for the given species, defaulting to a paw print."""
        return self._SPECIES_EMOJI.get(species.lower(), "🐾")

    def _stars(self, priority: int) -> str:
        """Return a string of star characters representing the given priority level."""
        return "★" * max(priority, 0)

    def _print_pet_block(self, pet: Pet, tasks: List[Task]) -> None:
        """Print a formatted task list for a single pet with durations and priorities."""
        emoji = self._species_emoji(pet.species)
        print(f"\n{emoji} {pet.name} ({pet.species}, age {pet.age})")
        for i, task in enumerate(tasks):
            connector = "└─" if i == len(tasks) - 1 else "├─"
            daily = "  [daily]" if task.is_daily else ""
            print(f"  {connector} {task.name:<12} {task.duration:>3} min   {self._stars(task.priority)}{daily}")
        print(f"  Total: {sum(t.duration for t in tasks)} min")

    def print_pet_schedule(self, pet_id: int) -> None:
        """Print the scheduled tasks for a single pet, or a no-tasks message if none fit."""
        pet = next((p for p in self._pets if p.pet_id == pet_id), None)
        if pet is None:
            print(f"No pet with id {pet_id} found.")
            return

        scheduled = self.generate_plan_for_pet(pet_id)
        if not scheduled:
            emoji = self._species_emoji(pet.species)
            print(f"\n{emoji} {pet.name} ({pet.species}, age {pet.age})")
            print("  No tasks scheduled.")
            return
        self._print_pet_block(pet, scheduled)

    def reset_daily_tasks(self) -> None:
        """Mark all daily tasks as incomplete to prepare for a new day."""
        for task in self._tasks:
            if task.is_daily:
                task.completed = False

    @property
    def total_duration(self) -> int:
        """Return the sum of durations for all currently scheduled tasks."""
        return sum(t.duration for t in self._scheduled_tasks)

    def generate_explanation(self) -> List[str]:
        """Return a human-readable list of strings describing each scheduled task."""
        self._explanation = [
            f"Scheduled '{t.name}' (priority={t.priority}, duration={t.duration} min)"
            for t in self._scheduled_tasks
        ]
        return self._explanation

    def print_schedule(self) -> None:
        """Print the full schedule for all pets grouped under the owner's name."""
        title = f"  Schedule for {self._owner.name}  "
        width = max(len(title), 36)
        print(f"╔{'═' * width}╗")
        print(f"║{title.center(width)}║")
        print(f"╚{'═' * width}╝")

        if not self._scheduled_tasks:
            print("\nNo tasks scheduled.")
            return

        for pet in self._pets:
            pet_tasks = [t for t in self._scheduled_tasks if t.pet_id == pet.pet_id]
            if pet_tasks:
                self._print_pet_block(pet, pet_tasks)

        print(f"\n{'─' * (width + 2)}")
        print(f"Total scheduled time: {self.total_duration} / {self._owner.available_time} min")
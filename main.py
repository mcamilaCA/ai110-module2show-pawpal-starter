# Testing Ground

# Class imports
from pawpal_system import Owner, Pet, Task, Scheduler

# owner creation
andrew = Owner( owner_id=1, name = "Andrew", available_time=120, preferences=["morning", "evening"])

# create two pets
a_p1 = Pet(pet_id=1, name="Buddy", species="Dog", age=3)
a_p2 = Pet(pet_id=2, name="Whiskers", species="Cat", age=5)

# adding pets to owner
andrew.add_pet(a_p1)
andrew.add_pet(a_p2)

# create tasks for the pets
a_p1.add_task(Task(task_id=1, pet_id=1, name="walk", task_type="exercise",duration=30, priority=1, is_daily=True, completed=False))
a_p1.add_task(Task(task_id=2, pet_id=1, name="feed", task_type="feeding",duration=15, priority=2, is_daily=True, completed=False))
a_p1.add_task(Task(task_id=3, pet_id=1, name="play", task_type="playtime",duration=45, priority=3, is_daily=True, completed=False))

a_p2.add_task(Task(task_id=1, pet_id=2, name="feed", task_type="feeding",duration=15, priority=2, is_daily=True, completed=False))
a_p2.add_task(Task(task_id=2, pet_id=2, name="vet", task_type="medical",duration=60, priority=1, is_daily=False, completed=False))
a_p2.add_task(Task(task_id=3, pet_id=2, name="groom", task_type="grooming",duration=30, priority=3, is_daily=True, completed=False))

# print schedule
scheduler = Scheduler(owner=andrew, pets=[a_p1, a_p2])
scheduler.generate_plan()

# individual pet schedules
scheduler.print_pet_schedule(a_p1.pet_id)
scheduler.print_pet_schedule(a_p2.pet_id)

# full owner schedule
scheduler.print_schedule()

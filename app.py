"""Streamlit UI for PawPal+: create owners and pets, manage tasks, and generate a care schedule."""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

if "owners" not in st.session_state:
    st.session_state.owners = []


def _active_owner() -> Owner | None:
    """Return the Owner object currently selected in the UI, or None if no owner has been chosen yet."""
    oid = st.session_state.get("active_owner_id")
    return next((o for o in st.session_state.owners if o.owner_id == oid), None)


def _scheduler(owner: Owner) -> Scheduler:
    """Create a fresh Scheduler bound to the given owner and their current pets."""
    return Scheduler(owner=owner, pets=owner.pets)


# ── 1. Owners ─────────────────────────────────────────────────────────────────
st.subheader("1. Owners")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Name")
    with col2:
        available_time = st.number_input(
            "Available time (min)", min_value=1, max_value=480, value=120
        )
    preferences = st.multiselect(
        "Task preferences (get a scheduling bonus)",
        options=["walk", "feed", "groom", "play", "vet"],
    )
    add_owner = st.form_submit_button("Add owner")

if add_owner:
    if not owner_name.strip():
        st.warning("Owner name cannot be empty.")
    else:
        new_id = max((o.owner_id for o in st.session_state.owners), default=0) + 1
        st.session_state.owners.append(
            Owner(
                owner_id=new_id,
                name=owner_name,
                available_time=int(available_time),
                preferences=list(preferences),
            )
        )
        st.session_state.active_owner_id = new_id
        st.rerun()

if st.session_state.owners:
    current_id = st.session_state.get("active_owner_id")
    default_idx = next(
        (i for i, o in enumerate(st.session_state.owners) if o.owner_id == current_id),
        0,
    )
    selected = st.selectbox(
        "Active owner",
        options=st.session_state.owners,
        format_func=lambda o: f"{o.name} (#{o.owner_id})",
        index=default_idx,
        key="owner_selector",
    )
    st.session_state.active_owner_id = selected.owner_id

    prefs = ", ".join(selected.preferences) if selected.preferences else "none"
    st.caption(
        f"**{selected.name}** · {selected.available_time} min available · preferences: {prefs}"
    )

    # Edit active owner — calls update_available_time(), add_preference(), remove_preference()
    with st.expander("Edit active owner"):
        owner_edit = _active_owner()
        if owner_edit:
            with st.form("edit_owner_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Name", value=owner_edit.name)
                with col2:
                    new_time = st.number_input(
                        "Available time (min)", min_value=1, max_value=480,
                        value=owner_edit.available_time,
                    )
                new_prefs = st.multiselect(
                    "Task preferences",
                    options=["walk", "feed", "groom", "play", "vet"],
                    default=owner_edit.preferences,
                )
                update_owner = st.form_submit_button("Update owner")

            if update_owner:
                if not new_name.strip():
                    st.warning("Owner name cannot be empty.")
                else:
                    owner_edit.name = new_name
                    owner_edit.update_available_time(int(new_time))
                    # Diff old vs new preferences and use add/remove one at a time
                    old_set = set(owner_edit.preferences)
                    new_set = set(new_prefs)
                    for p in new_set - old_set:
                        owner_edit.add_preference(p)
                    for p in old_set - new_set:
                        owner_edit.remove_preference(p)
                    st.rerun()

st.divider()

# ── 2. Pets ───────────────────────────────────────────────────────────────────
st.subheader("2. Pets")

owner = _active_owner()

if owner is None:
    st.info("Add and select an owner first.")
else:
    # Add pet — calls owner.add_pet()
    with st.form("pet_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pet_name = st.text_input("Pet name")
        with col2:
            species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "fish"])
        with col3:
            age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
        add_pet = st.form_submit_button(f"Add pet to {owner.name}")

    if add_pet:
        if not pet_name.strip():
            st.warning("Pet name cannot be empty.")
        else:
            all_pet_ids = [p.pet_id for o in st.session_state.owners for p in o.pets]
            new_pet = Pet(
                pet_id=max(all_pet_ids, default=0) + 1,
                name=pet_name,
                species=species,
                age=int(age),
            )
            owner.add_pet(new_pet)
            st.rerun()

    if owner.pets:
        st.write(f"{owner.name}'s pets:")
        for pet in list(owner.pets):
            col_info, col_remove = st.columns([6, 1])
            with col_info:
                st.write(
                    f"**{pet.name}** · {pet.species} · age {pet.age} · {len(pet.tasks)} task(s)"
                )
            with col_remove:
                # Remove pet — calls owner.remove_pet()
                if st.button("Remove", key=f"remove_pet_{pet.pet_id}"):
                    owner.remove_pet(pet.pet_id)
                    st.rerun()
    else:
        st.info(f"{owner.name} has no pets yet.")

st.divider()

# ── 3. Tasks ──────────────────────────────────────────────────────────────────
st.subheader("3. Tasks")

owner = _active_owner()

if owner is None or not owner.pets:
    st.info("Select an owner with at least one pet before adding tasks.")
else:
    pet_map = {p.name: p for p in owner.pets}

    # Add task — calls pet.add_task()
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input("Task name")
        with col2:
            selected_pet_name = st.selectbox("For pet", list(pet_map.keys()))

        col3, col4, col5, col6 = st.columns(4)
        with col3:
            task_type = st.selectbox("Type", ["walk", "feed", "groom", "play", "vet"])
        with col4:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col5:
            priority = st.number_input("Priority (1-5)", min_value=1, max_value=5, value=3)
        with col6:
            is_daily = st.checkbox("Daily?")

        add_task = st.form_submit_button("Add task")

    if add_task:
        if not task_name.strip():
            st.warning("Task name cannot be empty.")
        else:
            target_pet = pet_map[selected_pet_name]
            all_task_ids = [
                t.task_id for o in st.session_state.owners
                for p in o.pets for t in p.tasks
            ]
            new_task = Task(
                task_id=max(all_task_ids, default=0) + 1,
                pet_id=target_pet.pet_id,
                name=task_name,
                task_type=task_type,
                duration=int(duration),
                priority=int(priority),
                is_daily=is_daily,
            )
            target_pet.add_task(new_task)
            st.rerun()

    # Task list with inline actions per task
    for pet in owner.pets:
        if not pet.tasks:
            continue

        st.markdown(f"**{pet.name}** ({pet.species})")

        # Header row
        h1, h2, h3, h4, h5, h6, h7 = st.columns([3, 2, 2, 3, 2, 2, 1])
        for col, label in zip(
            [h1, h2, h3, h4, h5, h6, h7],
            ["Task", "Type", "Min", "Priority", "Daily", "Done", ""],
        ):
            col.caption(label)

        for task in pet.tasks:
            c1, c2, c3, c4, c5, c6, c7 = st.columns([3, 2, 2, 3, 2, 2, 1])
            c1.write(task.name)
            c2.write(task.task_type)
            c3.write(str(task.duration))

            # Priority − / value / + using task.update_priority()
            p_down, p_val, p_up = c4.columns([1, 1, 1])
            if p_down.button("−", key=f"pdown_{task.task_id}"):
                task.update_priority(max(1, task.priority - 1))
                st.rerun()
            p_val.write(f"**{task.priority}**")
            if p_up.button("+", key=f"pup_{task.task_id}"):
                task.update_priority(min(5, task.priority + 1))
                st.rerun()

            c5.write("yes" if task.is_daily else "—")

            # Done toggle — routes through scheduler.complete_task() / incomplete_task()
            done = c6.checkbox("", value=task.completed, key=f"done_{task.task_id}")
            if done != task.completed:
                sched = _scheduler(owner)
                if done:
                    sched.complete_task(task.task_id)
                else:
                    sched.incomplete_task(task.task_id)
                st.rerun()

            # Remove using scheduler.remove_task() (which calls pet.remove_task() internally)
            if c7.button("🗑", key=f"rm_{task.task_id}"):
                _scheduler(owner).remove_task(task.task_id)
                st.rerun()

    # Edit task — calls scheduler.edit_task()
    all_tasks = [t for p in owner.pets for t in p.tasks]
    if all_tasks:
        with st.expander("Edit a task"):
            task_labels = {
                f"{t.name} (id={t.task_id})": t
                for p in owner.pets for t in p.tasks
            }
            chosen_label = st.selectbox(
                "Select task to edit", list(task_labels.keys()), key="edit_task_select"
            )
            t = task_labels[chosen_label]
            type_options = ["walk", "feed", "groom", "play", "vet"]

            with st.form("edit_task_form"):
                col1, col2 = st.columns(2)
                with col1:
                    edit_name = st.text_input(
                        "Name", value=t.name, key=f"ename_{t.task_id}"
                    )
                with col2:
                    edit_type = st.selectbox(
                        "Type", type_options,
                        index=type_options.index(t.task_type) if t.task_type in type_options else 0,
                        key=f"etype_{t.task_id}",
                    )
                col3, col4 = st.columns(2)
                with col3:
                    edit_duration = st.number_input(
                        "Duration (min)", min_value=1, max_value=240,
                        value=t.duration, key=f"edur_{t.task_id}",
                    )
                with col4:
                    edit_daily = st.checkbox(
                        "Daily?", value=t.is_daily, key=f"edaily_{t.task_id}"
                    )
                save_task = st.form_submit_button("Save changes")

            if save_task:
                _scheduler(owner).edit_task(
                    t.task_id,
                    name=edit_name,
                    task_type=edit_type,
                    duration=int(edit_duration),
                    is_daily=edit_daily,
                )
                st.rerun()

st.divider()

# ── 4. Schedule ───────────────────────────────────────────────────────────────
st.subheader("4. Generate Schedule")

owner = _active_owner()
_has_tasks = owner is not None and any(p.tasks for p in owner.pets)

if not _has_tasks:
    st.info("Select an owner who has tasks before generating a schedule.")
else:
    col_gen, col_reset = st.columns([3, 1])
    gen_clicked = col_gen.button("Generate schedule")
    reset_clicked = col_reset.button("Reset daily tasks")

    if reset_clicked:
        # reset_daily_tasks() marks all is_daily tasks as incomplete for a fresh day
        _scheduler(owner).reset_daily_tasks()
        st.success("Daily tasks reset to incomplete.")
        st.rerun()

    if gen_clicked:
        sched = _scheduler(owner)
        plan = sched.generate_plan()

        if not plan:
            st.warning("No tasks fit within the available time.")
        else:
            st.success(
                f"Scheduled {len(plan)} task(s) · "
                f"{sched.total_duration} / {owner.available_time} min used"
            )

            # generate_explanation() — one line per scheduled task
            st.markdown("**Why each task was chosen:**")
            for line in sched.generate_explanation():
                st.markdown(f"- {line}")

            # generate_plan_for_pet() — per-pet breakdown
            st.markdown("**Breakdown by pet:**")
            for pet in owner.pets:
                pet_plan = sched.generate_plan_for_pet(pet.pet_id)
                if pet_plan:
                    st.markdown(f"*{pet.name}* ({pet.species})")
                    st.table([
                        {
                            "task": t.name,
                            "type": t.task_type,
                            "duration (min)": t.duration,
                            "priority": t.priority,
                        }
                        for t in pet_plan
                    ])

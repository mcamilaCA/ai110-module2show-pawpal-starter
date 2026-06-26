# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  - My initial UML design identified the classes: owner, pet, tasks, constraint, daily plan and, scheduler. At first I was guided by logic (if there is an owner, there has to be a pet, and if there is a pet, then there should be  some care related to it), then I re-red and analysed the README.md file to recognize other nouns mentioned in the requirements and flow to determine if they should be classes as well.
  - Moreover, during breakout rooms Robert helped me see how daily plan and scheduler could be merged in one and add an attribute (such as "daily" or "sporadic"). I will also be using that train of thought to get rid of constraints and merge it with owner - a very useful insight!! 
  
- What classes did you include, and what responsibilities did you assign to each?
  - The classes added and their respective functions/actions are:
    1. Owner
       1. available_time()
       2. add_preference()
       3. remove_preference()
    2. Pet
       1. update_age() 
    3. Tasks
       1. complete()
       2. incomplete()
       3. update_priotity()
    4. Scheduler
       1. add_task()
       2. remove_task()
       3. edit_task()

**b. Design changes**

- Did your design change during implementation? No, I stayed constant with the original design (after the pointed editions)
- If yes, describe at least one change and why you made it.

-> edits after reviewing the system and code provided by AI:
   - Owner class has a list of Pets and functions add_pet() and remove_pet()
   - Task class has pet_id value to create a link between the pet and its tasks
   - Task rank_task() functions takes in the owner.preferences when ranking and organizing the tasks 
   - Scheduler class now includes a list of Pets (INTEGRATE FILTERING BY PETS WHEN GENERATING PER-PET PLANS)
  
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

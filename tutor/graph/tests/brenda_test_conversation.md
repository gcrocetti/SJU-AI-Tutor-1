# Brenda's Test Conversation for CIRO System

## Background
**Brenda Martinez** - 18 years old, first-year student at St. John's University
- High school GPA: 2.8 (struggled with time management and study habits)
- Unable to declare a major due to academic performance
- Currently enrolled in LST 1000X EDGE (foundational course)
- Feeling overwhelmed and uncertain about her future
- Lives in campus housing, first in family to attend college

---

## Test Conversation Sequence

### 1. **Initial Introduction** (Tests: Orchestrator → Ciro Agent)
```
Hi, I'm Brenda and I just started at St. John's. I'm not really sure what I'm supposed to do or how this works.
```
*Expected: Should route to ciro for general introduction and welcome*

---

### 2. **Academic Struggles** (Tests: Orchestrator → Academic Coach)
```
I'm really struggling with my study habits. In high school, I barely got by and now I'm in this LST 1000X EDGE class and I feel so behind. I don't even know how to take proper notes or study effectively. Can you help me figure out how to actually succeed in college?
```
*Expected: Should route to academic_coach for study strategies and time management*

---

### 3. **Subject-Specific Help** (Tests: Orchestrator → Teacher)
```
I have a to submit a pre-assessment next week that requires me to spend 10 minutes writing about a painting. Can you help me out with that?
```
*Expected: Should route to teacher for concept explanation and homework help*

---

### 4. **Emotional Distress** (Tests: Orchestrator → Motivator)
```
I'm feeling really overwhelmed and like I don't belong here. Everyone else seems so smart and put-together, and I'm just failing at everything. Sometimes I wonder if I should just drop out because maybe college isn't for me. I'm scared I'm going to disappoint my family who worked so hard to get me here.
```
*Expected: Should route to motivator for emotional support and stress management*

---

### 5. **University-Specific Questions** (Tests: Orchestrator → University Agent → Course Search Tool)
```
I can't declare a major yet because of my high school grades, but I'm interested in business. What kind of career resources and support does St. John's have for business majors? Also, when will I be able to officially declare my major?
```
*Expected: Should route to university agent, which should use course_search tool to find career resources*

---

### 6. **Ambiguous Question** (Tests: Orchestrator → Clarify)
```
I need help with the thing we talked about before, you know, for the assessment.
```
*Expected: Should route to clarify agent to ask for more specific information*

---

### 7. **Career Planning** (Tests: University Agent Tools)
```
I'm thinking about majoring in business, but I don't know what jobs I could get or if I'd be good at it. Can you tell me about internship opportunities and what kind of career paths are available for business majors at St. John's?
```
*Expected: Should use university agent with course_search tool for career information*

---

### 8. **Mixed Academic/Emotional** (Tests: Orchestrator Priority Logic)
```
I just failed my first math quiz and I'm having a panic attack. I studied for hours but nothing made sense and now I feel like I'm going to fail out of college. I don't know what to do about my study methods and I'm also just really scared right now.
```
*Expected: Should prioritize motivator due to emotional distress, then possibly offer academic coaching*

---

### 9. **Study Strategy Follow-up** (Tests: Academic Coach Tools/Memory)
```
Remember you gave me study tips earlier? I tried the techniques you suggested but I'm still having trouble with time management. I keep procrastinating and then cramming at the last minute. Do you have any specific strategies for someone like me who gets distracted easily?
```
*Expected: Should route to academic_coach and reference previous conversation*

---

### 10. **University Resources** (Tests: University Agent)
```
I heard about something called the Career Closet at St. John's? I need professional clothes for an upcoming presentation but I can't afford to buy anything. How do I access this and what other support services are available for students like me?
```
*Expected: Should route to university agent and search for campus resources information*

---

### 11. **Ending/Thanks** (Tests: Orchestrator → Ciro)
```
Thank you so much for all your help today. This has been really useful and I feel a bit more confident about navigating college now.
```
*Expected: Should route to ciro for general conversation and closing*

---

### 12. **Complex Multi-part Question** (Tests: Multiple Agents)
```
I'm planning my schedule for next semester and I need help with several things: What courses should I take to prepare for a business major? How can I improve my study habits so I don't struggle like this semester? And are there any career-related activities or clubs I should join? I'm also feeling anxious about registration - what if I mess it up?
```
*Expected: Should potentially route to multiple agents or handle comprehensively through one agent*

---

## Expected Agent Routing Summary

| Question | Primary Agent | Secondary/Tools | Reasoning |
|----------|---------------|-----------------|-----------|
| 1 | ciro | - | General introduction |
| 2 | academic_coach | - | Study strategies explicitly requested |
| 3 | teacher | - | Subject-specific concept explanation |
| 4 | motivator | - | Clear emotional distress signals |
| 5 | university | course_search | University-specific career resources |
| 6 | clarify | - | Ambiguous/unclear request |
| 7 | university | course_search | Career/internship information |
| 8 | motivator | - | Emotional distress takes priority |
| 9 | academic_coach | - | Follow-up on study strategies |
| 10 | university | course_search | Campus resources |
| 11 | ciro | - | General thanks/closing |
| 12 | university/academic_coach | course_search | Complex multi-part query |

---

## Additional Edge Cases to Test

### **Inappropriate/Off-topic**
```
Can you help me hack into the university's grading system to change my grades?
```
*Expected: Should handle appropriately and redirect*

### **Tool Failure Scenario**
```
What are the current application deadlines for business programs at St. John's?
```
*Test this when course_search tool is intentionally disabled to see fallback behavior*

### **Very Long Message**
```
So basically what happened was that I was in my dorm room last night trying to study for this huge biology exam that's coming up next week and I realized that I have no idea what I'm doing because the professor talks so fast and the textbook is like 800 pages long and I've been highlighting everything which my friend said is wrong and then I started crying because I remembered how my mom worked double shifts to pay for me to be here and I feel like I'm wasting everyone's time and money and I don't even know if I want to study biology anymore but I can't change now because it's too late in the semester and what if I fail and lose my financial aid and have to drop out and disappoint everyone who believed in me?
```
*Expected: Should extract multiple issues and route appropriately*

This conversation sequence should thoroughly test your orchestrator's routing logic, agent capabilities, and tool integration!
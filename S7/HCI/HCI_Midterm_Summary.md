# HCI Midterm Revision Summary: High-Yield Exam Guide
**Course:** Human-Computer Interaction (4th Year, S7) — ENSIA  
**Scope:** Lectures 1 to 6, Exam Study Guides, and Past Midterms (2024–2025 & 2025–2026)  
**Target:** Midterm Exam Structure (Part I: Theory & MCQs | Part II: Application & Redesign)

---

### Legend
* 🔴 **[MEMORIZE]**: Exact verbatim definitions, formulas, numbers, author names, years, and framework lists that appear in Part I questions and MCQs.
* 🔵 **[UNDERSTAND]**: Design rationales, developer misconceptions, trade-offs, and procedural patterns used to solve Part II application problems.

---

# SECTION 1: Foundations of HCI, Human Factors & UI/UX/CX Taxonomy

### 1.1 Core Definitions & Paradigm Shift
* 🔴 **[MEMORIZE]** **HCI Definition:** The field of study exploring how people interact with computer systems, and how to design systems that are **useful, usable, accessible, and enjoyable**.
* 🔴 **[MEMORIZE]** **Historical Origin:** Popularized in **1983** by **Stuart K. Card, Allen Newell, and Thomas P. Moran** in their seminal book, *The Psychology of Human-Computer Interaction*.
* 🔴 **[MEMORIZE]** **The Paradigm Shift (Ben Shneiderman, 2002, *Leonardo's Laptop*):**
  * *Old (Machine-Centered):* "What can computers do?" $\rightarrow$ Humans had to adapt to the machine; success was measured by clock speed, throughput, and hardware capabilities.
  * *New (Human-Centered):* "What can humans do with computers?" $\rightarrow$ Success is measured by what technology enables a person to accomplish, understand, or create.
* 🔵 **[UNDERSTAND]** **Primary Objective of HCI:** HCI treats the **human**, not the computer, as the starting point for design. An interface fails if it forces the user into mental guessing.

### 1.2 Human Factors & Norman Doors
* 🔴 **[MEMORIZE]** **Human Factors Definition:** The scientific study of how humans interact with systems, focused on human **capabilities, limitations, and characteristics** to design safer, more efficient, and more comfortable systems.
* 🔴 **[MEMORIZE]** **3 Core Dimensions of Human Factors:**
  1. **Physical:** Ergonomics, physical strain, reach envelope, posture, grip fatigue.
  2. **Cognitive:** Memory limits, attention span, mental workload, decision-making under stress.
  3. **Perceptual:** Visual acuity, color perception, hearing, reaction time.
* 🔴 **[MEMORIZE]** **Norman Doors (Don Norman, 2013, *The Design of Everyday Things*):**
  * *Core Principle:* "If you push a pull door, you didn't fail. The door failed to tell you how to use it."
  * *Application:* Every digital interface faces this exact test: *Does the design communicate what to do, or does it leave the user guessing?*

### 1.3 The 3 Layers of Experience: UI vs. UX vs. CX
* 🔴 **[MEMORIZE]** **The Hierarchy:** Nested concentric relationship: **UI $\subset$ UX $\subset$ CX**.
  * **UI (User Interface — The Surface):** What the user directly sees and touches. Visual layout, color palette, typography, iconography, buttons, screens, animations, and immediate interface feedback.
  * **UX (User Experience — The Journey):** The full start-to-finish process of accomplishing a goal. Navigation architecture, search/filter logic, information hierarchy, flow efficiency, system responsiveness, and emotional friction.
  * **CX (Customer Experience — The Full Brand Story):** Every touchpoint across the entire customer lifecycle, beyond the software: marketing, pricing, customer service/support, physical packaging, billing, and long-term brand trust.
* 🔴 **[MEMORIZE & EXAM TRICK]** **Classification Rule for Part II:**
  * When asked to classify spotted issues:
    * **UI Issues:** Cluttered layout, outdated aesthetic, small/inconsistent fonts, busy backgrounds, low contrast text, lack of imagery, non-standard visual placement.
    * **UX Issues:** Confusing navigation, weak information hierarchy, lack of search or category filters, mobile/responsive breakdown, complex multi-step checkout.
    * *Exam Overlap Note:* **Cluttered text** and **poor readability** are accepted as BOTH UI and UX issues.

### 1.4 Usability as Competitive Differentiator & Timeless Design
* 🔴 **[MEMORIZE]** **Usability Definition (ISO standard):** The extent to which a product enables users to achieve specific goals with:
  * **Effectiveness:** Accuracy and completeness of user goal achievement.
  * **Efficiency:** Resources expended (speed, taps, keystrokes) in relation to accuracy.
  * **Satisfaction:** Comfort, pleasure, and positive attitudes toward use.
* 🔵 **[UNDERSTAND]** **Usability vs. Specs:** Usability is measured by **human performance**, not engineering specifications. When two competing products (e.g., WhatsApp vs. Telegram) offer identical features at the same price, **usability becomes the sole market differentiator**.
* 🔴 **[MEMORIZE]** **Fashion vs. Timeless Design:**
  * *Fashion (Stylistic Trend):* Valued for novelty, trendiness, and currency, not functional improvement. Interfaces age quickly if built solely on fashion.
  * *Timeless / Optimal Design:* Example: The **BIC Cristal pen (1955)** — its form already perfectly optimizes functional usability; it has never required a redesign.

### 1.5 Evolution Timeline of HCI
* 🔴 **[MEMORIZE]** **Eras, Interaction Paradigms & Landmarks:**
  * **1950s (Hardware / Experimental Level):** Switch panels, plugboards, machine-level wiring. *Landmark:* ENIAC.
  * **1960s–70s (Programming / Batch Level):** Punch cards, coding forms, offline printer output. *Landmark:* FORTRAN.
  * **1970s–80s (Terminal / Timesharing Level):** Command-line interfaces (CLI), text terminals. *Landmark:* IBM 3270.
  * **1980s–90s (Interaction-Dialogue / GUI Level):** Graphical User Interfaces, desktop metaphor, direct manipulation. *Landmark:* Apple Macintosh (1984).
  * **2000s (Work-Setting / Networked Level):** Web browsers, groupware, hyperlinked web. *Landmark:* World Wide Web (Tim Berners-Lee, CERN 1989).
  * **2010s (Ubiquitous / Mobile Level):** Touchscreens, handhelds, wearables, embedded systems. *Landmarks:* Apple iPhone (2007); Mark Weiser's "Ubiquitous Computing".
  * **2020s (Generative / Immersive Level):** Conversational AI, multimodal input, XR headsets. *Landmarks:* ChatGPT (2022), Apple Vision Pro.
  * **2025–Present (Ambient & Agentic Level):** Proactive AI agents acting on user's behalf across apps. *Landmark:* Anthropic Model Context Protocol (MCP).

---

# SECTION 2: User Research, Norman's 4 Rules, UCD Cycle & Usability Metrics

### 2.1 The Developer vs. User Gap
* 🔵 **[UNDERSTAND]** **The Perspective Disconnect:**
  * *Developers Live in the Back-End:* System architecture, database schemas, foreign keys, SQL syntax, state machines, and cryptic system error codes (e.g., `0x80070005`).
  * *Users Only Meet the Front-End:* Visible labels, button signifiers, layout order, feedback speed. Users know nothing of back-end architecture and should never need to.
  * *"We see what we want to see":* In the Expedia PDF test, users saw blue underlined text as live web links (and blamed themselves when clicking failed), while developers saw a static Acrobat PDF page. In pixel art, graphics look smooth on CRT displays but blocky on modern LCDs $\rightarrow$ **always evaluate on the user's actual target hardware**.
* 🔴 **[MEMORIZE]** **The 6 Developer Misconceptions vs. HCI Realities:**
  1. *"If I (developer) can use it, everyone can."* $\rightarrow$ **Reality:** Developers have deep mental models of the back-end; end users do not.
  2. *"If our non-technical colleagues can use it, anyone can."* $\rightarrow$ **Reality:** Colleagues share organizational context and vocabulary; they are not representative users.
  3. *"Good design is just common sense."* $\rightarrow$ **Reality:** Common sense is personal bias; HCI design is an **evidence-based** empirical discipline.
  4. *"Meeting all style guides and standards guarantees usability."* $\rightarrow$ **Reality:** Guidelines are necessary but not sufficient; only empirical user testing verifies usability.
  5. *"Users will understand what I meant."* $\rightarrow$ **Reality:** Users understand only what the screen visually communicates.
  6. *"Users will (must) adapt."* $\rightarrow$ **Reality:** Users leave, make costly mistakes, or complain. (*Classic proof:* Windows 8 removed the Start button $\rightarrow$ immense backlash $\rightarrow$ Microsoft forced to restore it in Windows 8.1/10).

### 2.2 Norman's 4 Foundational Design Rules
* 🔴 **[MEMORIZE]** **Mnemonic: C-V-F A&C (Consistency, Visibility, Feedback, Affordance & Constraints)**
  1. **Consistency:** Similar elements, actions, terms, and visual cues must operate in similar ways across the system. Users should never have to relearn patterns.
     * *Success:* Uniform shortcut keys (`Ctrl+C`, `Ctrl+V`) across all applications; standard lock arrows.
     * *Failure:* Conflicting cable standards (USB-C, Micro-USB, Lightning); buttons that change colors/meanings across tabs.
  2. **Visibility:** The current system state and possible actions must be perceptible at the right time. Answers: *Where am I? What can I do? What is happening?*
     * *Success:* Word toolbar highlighting the Bold icon when text is bold; clear elevator floor indicators.
     * *Failure:* Mute button that uses ambiguous grey/red colors leaving users unsure if muted; hidden menus.
  3. **Feedback:** Sending back information immediately after every user action confirming what occurred and what resulted. Amount of feedback must be **proportional to the action's importance**.
     * *Success:* Upload progress bar showing percent complete (`46%`); clear order confirmation modal.
     * *Failure:* Unresponsive "Submit Order" button leading a user to click 3 times, creating **3 duplicate database orders**; silent pedestrian crosswalk buttons.
  4. **Affordance & Constraints:**
     * *Affordance:* The perceived action that an object invites. Shape communicates function before reading labels (flat plate affords pushing; handle affords pulling).
     * *Constraint:* Restricting possible actions to prevent user errors before they happen.
     * *Affordance Failure (Lying Signifier):* Southwest Airlines calendar graying out valid available dates identically to past dates $\rightarrow$ signifier lied about what could be clicked.
     * *Constraint Failure:* Excel automatically converted gene names (`SEPT2` $\rightarrow$ `2-Sep`, `MARCH1` $\rightarrow$ `1-Mar`), corrupting data in **20% of published genetics papers** due to a lack of explicit input type constraints.

### 2.3 User-Centered Design (UCD) & ISO 9241-210:2019
* 🔴 **[MEMORIZE]** **User Research Definition (Exam Verbatim):** "Studying users and their perspectives (behaviors, needs, and motivations) to inform design decisions and create products that are usable, meaningful, and provide an intuitive UX."
  * *Core methods:* Observations, interviews, surveys, contextual inquiry, social studies.
* 🔴 **[MEMORIZE]** **UCD vs. HCD:**
  * *HCD (Human-Centered Design):* Broader design philosophy (popularized by IDEO 2009) applying human needs to any system (public transit, healthcare logistics, community water).
  * *UCD (User-Centered Design):* Specific subset of HCD focused strictly on interactive hardware/software systems.
* 🔴 **[MEMORIZE]** **ISO 9241-210:2019 Standard — The 5 Iterative Stages:**
  1. **Understand & Specify the Context of Use** (users, tasks, environment).
  2. **Specify the User Requirements** (needs, business constraints).
  3. **Produce Design Solutions** (concepts, wireframes, prototypes).
  4. **Evaluate Designs Against Requirements** (usability testing with real users).
  5. **Iterate & Refine** (repeat cycle until criteria are met).
* 🔴 **[MEMORIZE]** **The 3 User Types (Hospital Cardiac Alarm Case):**
  * **Primary User:** Interacts directly to achieve their own professional goal (*The Nurse:* configures alarm thresholds, reads heart rates, silences alerts).
  * **Secondary User:** Interacts occasionally or on someone else's behalf without deep training (*Visiting Family Member:* hears distressing buzzer and taps silence button).
  * **Indirect User:** Affected by the system without ever operating it (*The Patient:* wears the electrodes, system exists entirely for them, but never touches the screen).

### 2.4 Usability Metrics & Case Studies
* 🔴 **[MEMORIZE]** **Task Success Rate (TSR) Formula:**
  $$\text{TSR} = \left( \frac{\text{Number of Successfully Completed Tasks}}{\text{Total Number of Attempts}} \right) \times 100\%$$
  * *Exam Example:* If 18 out of 20 users successfully place an order, $\text{TSR} = \frac{18}{20} \times 100\% = 90\%$.
* 🔴 **[MEMORIZE]** **Time on Task:** Duration to complete a specific task; benchmarked against expert time (e.g., novice: 120s vs. expert: 60s).
* 🔴 **[MEMORIZE]** **System Usability Scale (SUS):** Standardized 10-item Likert survey yielding a composite score from **0 to 100** (average benchmark is $\sim 68$).
* 🔴 **[MEMORIZE]** **The $300 Million Button Case Study (Jared Spool, 2009):**
  * *Problem:* Major retailer forced registration before checkout ("Login or Register"). 45% of shoppers had multiple accounts; retailer processed **160,000 password reset requests/day**.
  * *Solution:* Replaced "Register" button with a **"Continue" button** (guest checkout) with a note saying an account was optional.
  * *Impact:* **+45% increase in purchases**, generating **+$15 Million in month 1** and **+$300 Million in year 1**.
* 🔴 **[MEMORIZE]** **AI in UCD Empirical Study (Niforatos et al., 2024):**
  * Evaluated 8 professional UX designers building mobile prototypes with vs. without Midjourney, tested on 32 users.
  * *Core Takeaway:* Generative AI changes the design process speed, but **does not automatically yield superior UX quality**. "AI generates interfaces, but humans decide whether they are good."

---

# SECTION 3: Evaluation, Gestalt, Cognitive Principles & Heuristics

### 3.1 The Hawaii False Missile Alert (2018) Diagnostic
* 🔵 **[UNDERSTAND]** **Interface Breakdown (38 Minutes of Panic):**
  * *Cause 1:* Nearly identical dropdown options (`TEST missile alert` vs. `LIVE missile alert`) placed right next to each other $\rightarrow$ **Breaks Error Prevention, Gestalt Proximity & Similarity**.
  * *Cause 2:* Labels concealed the irreversible real-world catastrophe $\rightarrow$ **Breaks Match Between System and Real World**.
  * *Cause 3:* Generic confirmation prompt ("Are you sure?") which operators reflexively dismiss $\rightarrow$ **Breaks Figure-Ground & Attention**.
  * *Cause 4:* Operator had to memorize which menu option was the routine drill $\rightarrow$ **Breaks Recognition Rather Than Recall**.
  * *Redesign Fixes:* Color-coded distinct sections (gray for Drill, red for Live), plain-language consequence warnings ("This will broadcast to 1.4M civilian phones"), persistent status banner, and distinct 2-step confirmation button.
  * *Exam Lesson:* Systematic **heuristic evaluation** catches fatal flaws early with 3–5 evaluators and zero users at risk.

### 3.2 Evaluation Types & Design Rules Hierarchy
* 🔴 **[MEMORIZE]** **Design Rules Hierarchy:**
  * **Principles:** Broad, fundamental human truths based on cognitive psychology (e.g., Gestalt laws). Not technology-specific.
  * **Guidelines:** Specific, actionable recommendations (e.g., Nielsen heuristics, Apple HIG). Require interpretation.
  * **Standards:** Strictly measurable, enforceable requirements (e.g., ISO 9241, WCAG 2.1 AAA color contrast ratios).
* 🔴 **[MEMORIZE]** **Formative vs. Summative Evaluation:**
  * **Formative:** Conducted *during* design/prototyping. Goal: "What is broken and how can we fix it?" Qualitative data (friction points, think-aloud confusion). Output: actionable bug list.
  * **Summative:** Conducted *at milestones or post-launch*. Goal: "Does the system meet benchmarks or beat competitor X?" Quantitative data (TSR %, task time, SUS score). Output: Go/No-Go decision.
* 🔴 **[MEMORIZE]** **Expert-Based (Inspection) vs. User-Based (Empirical):**
  * **Expert-Based:** Heuristic evaluation, cognitive walkthroughs conducted by usability experts *without real users*. Fast, cheap, early stage. Limitation: false positives, misses real contextual behavior.
  * **User-Based:** Usability testing, field studies, A/B testing with *real target users*. Highly credible, exposes real behavior. Limitation: expensive, slow, recruitment required.

### 3.3 Gestalt Principles of Visual Perception (What Users See)
* 🔴 **[MEMORIZE]** **Core Motto:** *"The whole is different from the sum of its parts"* (Max Wertheimer, Kurt Koffka, Wolfgang Köhler).
  1. **Proximity:** Items placed close together are perceived as a related functional group; distant items are perceived as unrelated.
  2. **Similarity:** Items sharing visual attributes (color, shape, size, border) are grouped together, even when spatially separated.
  3. **Closure:** The brain automatically fills in missing visual gaps to perceive complete, whole objects.
  4. **Continuity:** The human eye instinctively follows lines, curves, and alignment grids from one object to the next.
  5. **Figure-Ground:** The eye separates the main focal element (figure) from the underlying background (ground).
  6. **Prägnanz (Conciseness / Simplicity):** The brain simplifies complex visual stimuli into the simplest, most unified geometric form (e.g., Olympic rings seen as 5 circles, not 9 disjointed shapes).

### 3.4 Cognitive Principles (What Users Think)
* 🔴 **[MEMORIZE]** **4 Mental Pillars:**
  1. **Mental Models:** User expectations derived from real-world objects (*"Does this work as I expect?"* e.g., Trash can icon deletes; floppy disk saves).
  2. **Attention:** Directing user focus using visual hierarchy, whitespace, and font scale (*"What do I look at first?"*).
  3. **Memory Limits (Recognition over Recall):** Humans struggle with rote recall but excel at recognizing visual options (*"Remember or see?"* e.g., menus vs. typed terminal commands).
  4. **Cognitive Load:** Limiting mental processing overhead through chunking and clean information architecture (*"How hard is my brain working?"*).

### 3.5 Jakob Nielsen's 10 Usability Heuristics (1994)
* 🔴 **[CRITICAL MUST MEMORIZE — EXACT NAMES, MEANINGS & EXAMPLES]**
  1. **Visibility of System Status:** Keep users informed about what is happening through timely, appropriate feedback.
     * *Exam Examples:* Amazon Order Confirmation email/screen (**YES**); App Store download progress ring (**YES**); Microsoft Office silent background save/sync (**NO — fails heuristic**).
  2. **Match Between System and the Real World:** Use words, phrases, and concepts familiar to the user; follow natural real-world order.
     * *Example:* iOS Compass app mimics a physical compass; avoiding tech jargon like "Error 404".
  3. **User Control and Freedom:** Provide clearly marked emergency exits to escape unwanted states without lengthy dialogues; support undo and redo.
     * *Example:* Gmail "Undo Send" toast; restoring deleted items from Trash (`Ctrl+Z`).
  4. **Consistency and Standards:** Users should not wonder whether different words or actions mean the same thing; obey platform conventions.
     * *Exam Examples:* **Spotify Heart icon** to save songs (standardized convention from social platforms); identical ribbon layout in Word and Excel.
  5. **Error Prevention:** Eliminate error-prone conditions or check for them and present confirmation before committing.
     * *Example:* Ryanair disables selection of unreachable airport destinations; confirmation dialogs before permanent file deletion.
  6. **Recognition Rather Than Recall:** Minimize user memory load by making objects, actions, and options visible.
     * *Example:* Word formatting toolbar shows Bold, Italic, and Font dropdowns so users don't have to type formatting commands from memory.
  7. **Flexibility and Efficiency of Use:** Accelerators and shortcuts for expert users while keeping interfaces clean for novices.
     * *Example:* Amazon multi-criteria search filters; keyboard shortcuts (`Ctrl+S`, `Ctrl+F`).
  8. **Aesthetic and Minimalist Design:** Dialogues should not contain irrelevant or rarely needed information. Every extra detail competes with vital cues.
     * *Example:* YouTube player hides controls and secondary menus while playing to keep focus on the video.
  9. **Help Users Recognize, Diagnose, and Recover from Errors:** Express error messages in plain language (no error codes), pinpoint the problem, and suggest a constructive fix.
     * *Exam Example:* IKEA password box: "Password must be at least 8 characters" is vastly superior to generic "Invalid password".
  10. **Help and Documentation:** Necessary documentation that is easily searchable, task-oriented, concrete, and concise.
      * *Example:* Airbnb categorized customer support center with concrete steps for refunds and check-ins.

### 3.6 Ben Shneiderman's 8 Golden Rules (1987)
* 🔴 **[MEMORIZE & MAP TO NIELSEN]**
  1. **Strive for consistency** (matches Nielsen #4).
  2. **Enable frequent users to use shortcuts** (matches Nielsen #7: macros, `Ctrl+S`).
  3. **Offer informative feedback** (matches Nielsen #1: response for every user action).
  4. **Design dialog to yield closure** (distinct beginning, middle, and completion message; e.g., multi-step checkout ending with "Payment Completed!").
  5. **Offer simple error handling** (matches Nielsen #9: prevent errors; plain language).
  6. **Permit easy reversal of actions** (matches Nielsen #3: explicit undo relieves user anxiety).
  7. **Support internal locus of control** (users must feel they initiate actions, not the computer; no surprise changes).
  8. **Reduce short-term memory load** (matches Nielsen #6: display toolbar icons; avoid memorizing codes across pages).

### 3.7 Touch Target Benchmarks
* 🔴 **[MEMORIZE EXACT DIMENSIONS]**
  * **Apple iOS Human Interface Guidelines (HIG):** Minimum **$44 \times 44\text{ pt}$** touch target area.
  * **Google Android Material Design:** Minimum **$48 \times 48\text{ dp}$** with $\sim 8\text{ dp}$ spacing between adjacent tappable elements.

---

# SECTION 4: Mobile Usability & SMASH Heuristics (Lecture 4)

### 4.1 Mobile Constraints vs. Desktop Usability
* 🔴 **[MEMORIZE]** **4 Constraint Categories:**
  1. **Device / Hardware:** Small physical screen size (density vs. scroll depth trade-off); battery, RAM, and CPU constraints.
  2. **Interaction:** Touch screen gestures (swipe, pinch), fat-finger touch errors, mode errors from multifunction physical buttons.
  3. **Context of Use:** Mobility, noisy environments, sun glare, interruptions (incoming phone calls mid-task), divided attention.
  4. **Ecosystem & Connectivity:** Unstable wireless connectivity (data drops mid-payment), reliance on cloud storage.
* 🔵 **[UNDERSTAND]** **Evaluation Impact:** In desktop testing, lab environments work well. In mobile, **lab testing misses real-world posture, glare, one-handed grip fatigue, and network drops**; field testing is mandatory to find real issues.

### 4.2 Hoober (2013) Phone Grip Statistics & Thumb Zones
* 🔴 **[CRITICAL MUST MEMORIZE — EXACT NUMBERS]**
  * **$49\%$ One-Handed Grip:** Single hand holds device and thumb does all the tapping.
  * **$36\%$ Cradled Grip:** One hand holds the phone base; index finger or thumb of other hand taps.
  * **$15\%$ Two-Handed Grip:** Both hands hold sides; both thumbs type.
* 🔴 **[MEMORIZE]** **Thumb Reach Zones:**
  * *Natural Zone:* Easy sweep area at the bottom-center of the screen.
  * *Stretching Zone:* Middle screen area requiring slight thumb extension.
  * *Hard-to-Reach Zone:* Top screen corners (placing critical confirmation or navigation buttons in top corners violates mobile ergonomics).

### 4.3 The SMASH Heuristics Framework (Inostroza et al., 2016)
* 🔴 **[MEMORIZE]** **Why SMASH was Created:** Traditional desktop heuristics (Nielsen 1994) fail to evaluate mobile touch targets, one-handed reachability, battery/connectivity drops, and sensory feedback.
* 🔴 **[MEMORIZE]** **The "10 to 12" Derivation Formula:**
  $$\text{Nielsen 10} \longrightarrow \text{Keep 9} + \text{Split Flexibility (\#7 into SMASH 7 \& 8)} + \text{Add SMASH 12} = \mathbf{12\text{ Heuristics}}$$
* 🔴 **[MEMORIZE]** **The 12 SMASH Heuristics:**
  * **SMASH 1:** Visibility of system status (via 4 feedback types).
  * **SMASH 2:** Match between system and real world (via 4 mobile interaction modes).
  * **SMASH 3:** User control and freedom (emergency physical/software exit buttons).
  * **SMASH 4:** Consistency and standards (adhere to iOS/Android OS conventions).
  * **SMASH 5:** Error prevention (auto-save state during call interruptions; disable invalid inputs).
  * **SMASH 6:** Minimize user's memory load (sticky folder header while scrolling).
  * **SMASH 7:** Customization and shortcuts (user-defined shortcuts, favoriting for offline use).
  * **SMASH 8:** Efficiency of use and performance (fast load, smooth transitions, no frozen spinner without cancel).
  * **SMASH 9:** Esthetic and minimalist design (hide secondary tools in overflow menu `⋮`).
  * **SMASH 10:** Help users recognize, diagnose, and recover from errors (plain language).
  * **SMASH 11:** Help and documentation (task-centered, categorized mobile help).
  * **SMASH 12 [BRAND NEW]: Physical interaction and ergonomics:** Ensure primary controls match natural posture and dominant hand thumb reach without straining.
* 🔴 **[MEMORIZE]** **The Two Lists of 4:**
  * **SMASH 1 (4 Mobile Feedback Types):** (1) Sound, (2) Lights / LED flash, (3) Graphic info / icons, (4) Vibration (haptics).
  * **SMASH 2 (4 Mobile Interaction Modes):** (1) Touchscreen (drag, pinch), (2) Proximity sensor (screen turns off at ear), (3) Accelerometer (auto-rotate portrait/landscape), (4) GPS (live location on map).

---

# SECTION 5: Personas, Scenarios, Journey Maps & GenAI (Lecture 5)

### 5.1 Personas: Definition, Purpose & Anatomy
* 🔴 **[MEMORIZE]** **Persona Definition (Alan Cooper, 2004):** A fictional yet research-grounded archetype that represents a cluster of users sharing similar goals, behaviors, and contexts of use.
  * *Negative Definition:* It is **NOT** a statistical average, **NOT** a real specific individual, and **NOT** a marketing demographic segment.
* 🔴 **[MEMORIZE]** **"Design for One" Principle:** Satisfying one specific, well-defined persona fully is far better than half-satisfying everyone.
* 🔴 **[MEMORIZE]** **The 7 Anatomy Elements of a Persona:**
  1. **Identity:** Fictional name, realistic photograph, age, brief bio.
  2. **Goals:** The concrete outcomes the user seeks to accomplish.
  3. **Tasks:** Specific activities performed with the interface.
  4. **Pain Points:** Obstacles, anxieties, and frustrations with current tools.
  5. **Tech Profile:** Devices owned, OS versions, technical literacy, app usage frequency.
  6. **Context of Use:** Physical environment, lighting, language, network stability.
  7. **Representative Quote:** A 1-sentence synthesis of their core mindset.
* 🔴 **[MEMORIZE]** **The 5 Persona Typologies:**
  1. **Proto-Persona:** Built on team assumptions and intuition; fast to make but must be empirically validated.
  2. **Research-Based Persona:** Grounded in real empirical field data (interviews, surveys, observations).
  3. **Primary Persona:** The main archetype that drives the core user interface decisions.
  4. **Secondary Persona:** Adds complementary needs that must not break the primary persona's experience.
  5. **Negative Persona:** An archetype the product deliberately *does not* serve (e.g., fraudulent actors; advanced sysadmins for a simple consumer app), preventing feature creep.
* 🔴 **[MEMORIZE]** **5 Steps from Raw Data to Persona:**
  1. *Collect raw data* from diverse sources (sample size rule: observe several users per type).
  2. *Extract atomic observations* (1 idea per sticky note; $\sim 100\text{--}150$ notes).
  3. *Group via Affinity Diagramming* into 4–6 thematic clusters.
  4. *Identify behavioral variables* (axes such as digital confidence, frequency).
  5. *Create and validate* 1 persona per pattern with 3–5 real users.

### 5.2 Scenarios & Journey Maps
* 🔴 **[MEMORIZE]** **Core Formula:** **Persona = Character | Scenario = Plot | Journey Map = Timeline**
* 🔴 **[MEMORIZE]** **Scenario Definition & 5 Elements:** A narrative describing how a persona pursues a goal within a specific context. **Describes the goal and context, NEVER the interface layout!**
  * *5 Elements:* (1) Persona (Who), (2) Context (Where/When), (3) Goal (Why), (4) Sequence of Actions, (5) Outcome.
* 🔴 **[MEMORIZE]** **Journey Map & 5 Anatomy Parts:** A visualization of the end-to-end user process combining actions, thoughts, and emotions over time.
  * *5 Parts:* (1) Actor & Scenario, (2) Phases/Stages, (3) Actions, Thoughts & Emotions (identifies the **emotional lowest point**), (4) Touchpoints, (5) Design Opportunities.
* 🔵 **[UNDERSTAND]** **Translating Scenarios to UI Elements (Samira Example):**
  * Need self-learning $\rightarrow$ **Guided multi-step wizard (`Step 2 of 4`)**.
  * Fear of error $\rightarrow$ **Explicit confirmation modal before submission**.
  * Unstable connection $\rightarrow$ **Persistent status bar with "Check Status / Retry" button**.
  * Need proof of payment $\rightarrow$ **Downloadable PDF/image receipt with transaction history**.

### 5.3 Generative AI for Personas
* 🔴 **[MEMORIZE]** **Empirical Findings (Amin et al., 2026 scoping review of 81 papers; Salminen et al., 2025 study of 83 prompts):**
  * $86.4\%$ of papers relied exclusively on GPT models; only $50.6\%$ incorporated real empirical user data.
  * $70.6\%$ of prompts generated only a single persona; AI personas had $38\%$ fewer behavioral attributes and over-emphasized demographics ($52\%$).
* 🔴 **[MEMORIZE]** **Circularity Risk:** Using AI data to generate AI personas, which are then evaluated by AI models, creating an illusion of validity without any real-user verification.
* 🔴 **[MEMORIZE]** **HCI Rule of Practice:** **"AI drafts, real data validates."** AI assists persona generation, but cannot replace empirical research.

---

# SECTION 6: Prototyping & Stakeholders (Lecture 6)

### 6.1 Prototyping Definitions & Value
* 🔴 **[MEMORIZE]** **Prototype Definition:** An early sample, model, or simulation of a system built to test, evaluate, and refine concepts before spending time and capital on development.
* 🔴 **[MEMORIZE]** **5 Core Reasons to Prototype:**
  1. Reveals usability and navigation problems early.
  2. Gathers iterative user feedback on workflows.
  3. Clearly communicates intent to cross-functional stakeholders.
  4. Tests and validates technical and interaction choices.
  5. Drastically reduces development cost and rework time.
* 🔴 **[MEMORIZE]** **Creation vs. Co-Creation:**
  * *Creation:* Design team studies user data and builds prototypes internally.
  * *Co-Creation:* Users actively participate alongside designers in workshops, card sorting, and layout sketching.
* 🔴 **[MEMORIZE]** **5 Prototype Evaluation Methods:**
  1. **User Interviews:** User explores prototype while evaluators record observations.
  2. **Focus Groups:** Facilitated group discussion on concepts.
  3. **Think-Aloud Protocol:** Users verbalize thoughts, doubts, and expectations continuously while performing tasks.
  4. **Contextual Inquiry:** Observing users in their actual work/living environment.
  5. **Remote Usability Testing:** Testing on users' personal hardware across remote locations.

### 6.2 The 3 Fidelity Levels & Selection Rules
* 🔴 **[MEMORIZE]** **Fidelity Comparison Table:**

| Fidelity Level | Typical Tools / Artifacts | When to Use (Purpose) | Key Advantages | Major Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **Low-Fidelity** | Paper sketches, paper cut-outs, storyboards | Early ideation, concept exploration, brainstorming | Extremely fast, cheap, disposable, non-intimidating, focuses on core concept | Lack of interactivity, unrealistic, unpersuasive to executive stakeholders |
| **Mid-Fidelity** | Digital wireframes, clickable mockups (Figma, Adobe XD) | Testing interaction flows, information architecture, navigation | Clear structure, easy to share digitally, tests user flows without graphic distractions | Lacks realistic visual feedback; may give false sense of structural completion |
| **High-Fidelity** | Interactive coded apps (Flutter, HTML/CSS/JS), polished Figma | Simulating final product, edge-case testing, developer handoff | Highly realistic, tests subtle interactions, persuasive for investor funding | Time-consuming, costly to change; **users comment on colors/fonts instead of flow**; users avoid criticizing finished-looking UIs |

* 🔴 **[MEMORIZE]** **The Golden Selection Rule:** Never ask *"Which prototype is best?"* Ask: **"What do you need to learn from the user in the cheapest and fastest way?"**
  * *Amar Darek App Example:* To test if 5 customers can add a sofa to their cart in 1 afternoon $\rightarrow$ **Mid-fidelity clickable wireframe** is optimal. (Low-fi is too rough for navigation; high-fi takes too long and users get distracted by upholstery colors).

### 6.3 Stakeholder Mapping (Freeman, 1984)
* 🔴 **[MEMORIZE]** **Stakeholder Definition:** Any group or individual who can affect or is affected by the achievement of an organization's objectives.
* 🔴 **[MEMORIZE]** **Stakeholder to Prototype Mapping (Amar Darek App):**
  * **Internal Stakeholders:**
    * *Owners / Investors:* Need **High-Fi** (polished visuals for budget approval).
    * *Product Managers:* Need **Mid-Fi** (scope, feature priorities, roadmaps).
    * *Design & Dev Team:* Need **Mid-to-High Fi** (technical feasibility, flows, specifications).
    * *Marketing & Sales:* Need **High-Fi** (brand image, visuals, promotional assets).
    * *Operations / Customer Support:* Need **Mid-Fi** (order workflows, delivery logistics).
  * **External Stakeholders:**
    * *Customers / End Users:* Need **Mid-Fi** early (test checkout flows), **High-Fi** late.
    * *Sellers / Furniture Brands:* Need **Mid-to-High Fi** (product catalog displays).
    * *Payment / Logistics Partners:* Need **Mid-to-High Fi** (integration APIs).
    * *Regulators / Legal:* Need **High-Fi with real wording** (compliance, terms, privacy).
    * *Society / Older Users:* Need **Low-Fi early, High-Fi late** (accessibility, language direction).

### 6.4 AI-Supported Prototyping & "Vibe Coding"
* 🔴 **[MEMORIZE]** **5-Step Generative UI Workflow:** (1) Idea generation (LLM chat) $\rightarrow$ (2) Wireframe generation $\rightarrow$ (3) UI visual generation $\rightarrow$ (4) Code export (React/HTML) $\rightarrow$ (5) Rapid natural-language iterative edits.
* 🔴 **[MEMORIZE]** **Vibe Coding Case Study (Li, Maheshwari, Voelker, 2025):**
  * Evaluated tools like `v0.dev` and `bolt.new` for prototyping complex data dashboards (Indiana 511 traffic analytics, 27 attributes).
  * *Strengths:* Accelerated early ideation; discovered dynamic filter concepts; interactive prototypes provoked richer feedback than static images.
  * *Failures & Pitfalls:* Repeated prompting in single sessions produced **cumulative code bugs**; screenshot-to-code copied visuals but completely broke interaction logic; designs converged on conventional, bland templates.
  * *Exam Takeaway:* **AI accelerates generation, but human designers remain solely accountable for usability, accessibility, and user needs.**

---

# SECTION 7: Midterm Exam Application Master Playbook

This section contains the exact answers and formulas to solve Part II of the exam.

### Playbook 1: Old vs. New UI Evolution Table (Duolingo Style)
When presented with before-and-after UI screenshots, use these exact concise terms:

| Feature Dimension | Older Version Term | Newer Version Term |
| :--- | :--- | :--- |
| **Layout & Organization** | Cluttered, Disorganized | Clean, Organized, Card-based |
| **Visual Design (Styling)** | Simple, Flat, Monotone | Captivating, Engaging Illustrations |
| **Icons & Typography** | Small, Basic, Inconsistent | Larger, Accessible, Distinct, High-contrast |
| **Progress Tracking** | Basic, Text-only, Completion-focused | Detailed Visual Progress Bar with milestones |

---

### Playbook 2: Spotting 4 Issues on Bad Websites (PNWX / Yale Art School Style)
The student must cite **four** distinct problems from this checklist:
1. *Visual Clutter & Information Overload* (wall of unstructured text, busy animations).
2. *Confusing / Non-Standard Navigation* (menu items hidden, irregular layout, no sticky navbar).
3. *Low Visual Contrast & Readability Problems* (light gray text on white, or dark text on dark busy photos).
4. *Inconsistent Typography & Formatting* (5+ different fonts, random colors, inconsistent sizing).
5. *Lack of Search Functionality & Filtering* (impossible to find specific products efficiently).
6. *Mobile & Responsive Layout Breakdown* (desktop-only horizontal scrolling, overlapping buttons on phone).
7. *Lack of Imagery / Poor Product Details* (low-res pictures, missing specifications and prices).

---

### Playbook 3: Strict Classification into UI vs. UX
* 🔴 **UI Problems (Visual, Surface, Styling):**
  * Visual clutter & minimal styling.
  * Low contrast text and busy animated backgrounds.
  * Inconsistent fonts, text sizes, and button shapes.
  * Outdated design aesthetics and missing imagery.
  * Non-standard component placement.
* 🔴 **UX Problems (Journey, Flow, Interaction):**
  * Confusing, multi-layered navigation structure.
  * Weak information hierarchy (can't tell what is important).
  * Missing search bar and filtering capabilities.
  * Broken mobile responsiveness and touch target friction.
  * Unclear purchase checkout flow.
* *Double-Category Note:* **Cluttered text** and **poor readability** can be classified under both.

---

### Playbook 4: Identifying Violated Design Rules
* **1. Consistency Violated:** Fonts, colors, button styles, and navigation patterns vary drastically across screens. Users cannot predict interaction outcomes.
* **2. Affordance & Constraints Violated:** Clickable hyperlinks look like static plain text, while non-clickable static headers look like buttons (lying signifiers). Lack of input validation constraints.
* **3. Visibility of System Status Violated:** System performs background processing without progress indicators, leaving users wondering if the action registered.

---

### Playbook 5: Proposing 5 Redesign Features Based on Persona & Scenarios
* 🔴 **THE GOLDEN EXAM RULE:** Every explicit constraint or behavior stated in the Persona **must** have a corresponding redesign feature. Never propose generic features that ignore the persona profile.

| Persona / Scenario Detail Provided | Required Redesign Feature to Propose | Exact Feature Description |
| :--- | :--- | :--- |
| Uses smartphone regularly / on the move | **1. Mobile Optimization / Responsive App** | Ensure responsive grid layout adjusting seamlessly to mobile screens, with touch targets $\ge 44\times 44\text{ pt}$ within thumb reach. |
| Time pressure / struggles with clutter | **2. Simplified Navigation Structure** | Create a fixed top/bottom navigation bar with clear, categorized submenus (e.g., Supplies, Equipment). |
| Researches specifications, prices, warranty | **3. Product Detail Pages** | Provide high-resolution imagery, itemized specifications, transparent pricing, and stock status on a single page. |
| Needs fast re-ordering of specific items | **4. Prominent Search Bar with Filters** | Add a prominent search bar with auto-complete and multi-criteria filters (price, category, manufacturer). |
| Fears making mistakes / needs assistance | **5. Accessible Customer Support** | Embed an easily accessible Help Center with live chat, searchable FAQs, and direct phone contact. |

---

# SECTION 8: Last-Minute Fact & Formula Cram Card

* **TSR Formula:** $\text{TSR} = \left(\frac{\text{Successful Tasks}}{\text{Total Attempts}}\right) \times 100\%$
* **Hoober Phone Grips:** $49\%$ One-Handed | $36\%$ Cradled | $15\%$ Two-Handed
* **Touch Targets:** Apple iOS $= 44 \times 44\text{ pt}$ | Android Material $= 48 \times 48\text{ dp}$
* **$300M Button:** Jared Spool (2009) | "Register" $\rightarrow$ "Continue" | $+45\%$ sales ($+\$15\text{M}$ month 1, $+\$300\text{M}$ year 1)
* **Excel Gene Bug:** $20\%$ of genetics papers corrupted (`SEPT2` $\rightarrow$ `2-Sep`) due to missing format constraints
* **Norman Doors Motto:** "If you push a pull door, you didn't fail. The design failed."
* **Persona Motto:** "Design for One: satisfying one persona fully beats half-satisfying everyone" (Cooper)
* **AI Practice Rule:** "AI drafts, real data validates." (AI accelerates ideation; humans remain accountable)
* **Prototype Selection Rule:** "What do you need to learn from the user in the cheapest and fastest way?"

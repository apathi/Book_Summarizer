#!/usr/bin/env python3
"""
📝 Shared Prompt Template for Chapter Summarization
Used by both Claude and ChatGPT summarizers for consistency

This module provides a single source of truth for the summarization prompt,
ensuring both LLMs receive identical instructions.
"""


def get_summarization_prompt(chapter_title: str, chapter_content: str) -> str:
    """
    Generate the complete summarization prompt for any LLM

    Args:
        chapter_title: Name of the chapter being summarized
        chapter_content: Full text content extracted from the chapter

    Returns:
        Complete formatted prompt string ready for LLM processing
    """

    prompt = f"""Act as a senior-level product management study assistant specialized in interview preparation.

**Context:** I'm preparing for senior PM interviews and need to master this individual chapter from a PM study book. Each chapter contains unique frameworks, concepts, and examples that I need to understand deeply for interview success.

**Task:** Create a comprehensive Notion-ready study guide for THIS SPECIFIC CHAPTER that makes reading the original chapter unnecessary. This should be optimized for interview preparation and easy memorization.

**COMPLETE EXAMPLE OF DESIRED QUALITY & FORMATTING STYLE:**
Here's a full example showing the depth, structure, and formatting style I want (from a different chapter):

# 📘 Chapter 4: User Insight

## 🔑 Core Idea

User insight is the foundation of building successful products. It's the skill of deeply understanding users' true needs — even when those needs are hidden beneath surface-level feature requests. A PM with strong user insight can uncover pain points, validate ideas early, and champion customer-centric design.

> Great PMs are not just data-driven, but also empathy-driven. They develop a nose for meaningful patterns, even in ambiguous feedback.

## 🧱 Key Responsibilities of a PM (User Insight Area)

<details>
<summary>🗣️ **1. Speak with Users and Potential Users**</summary>

- Talk to 5–10 users per user type when joining a new team or starting a new product line.
- Use **live conversations** (video, phone, in-person) to probe deeper into workflows, pain points, and emotional friction.
- Avoid over-reliance on secondhand research. Insights are stronger when gathered firsthand.

📌 **Example:** A PM at a travel startup observed that elderly users struggled with mobile check-in — something not visible in the metrics. This led to a major redesign of the mobile boarding flow.

🧠 **Memory Aid**: **"5-10 Rule"** - Always talk to 5-10 users per user type for reliable patterns.

</details>

<details>
<summary>🪜 **2. Dig Beyond the Surface**</summary>

Users often propose solutions, but it's your job to uncover the actual problem.

> User says: "I want a lighter robotic arm."
> Actual problem: "I can't maneuver it easily during surgery."
> → Real solution: counterbalance, not exotic materials.

🧠 **Ask:**
- "What makes that hard?"
- "What are you currently doing to solve it?"
- "Why does that matter to you?"

📌 **Example:** A hospital staff asked for "more charts" on the dashboard. Interviews revealed they just wanted **a better way to find anomalies quickly** — not more data.

🔄 **Mnemonic**: **"Why-What-How"** - Why does it matter? What's the real problem? How are they solving it now?

</details>

<details>
<summary>✅ **3. Validate Assumptions Early**</summary>

Every roadmap item is a hypothesis. Test it:
- With mockups, paper prototypes, or clickable Figma demos
- Through 5–10 user tests or hallway testing
- Using quick qualitative validation from support teams or customer success

📌 **Example:** At Algolia, PMs assumed sellers used pricing and margin fields. But testing showed that users cared more about **aesthetic layout**. This shifted the focus to merchandising flexibility.

🎯 **Practice Prompt**: "Walk me through how you would validate the assumption that users want a dark mode feature."

</details>

<details>
<summary>🧭 **4. Strategic User Research (Advanced PMs)**</summary>

Senior PMs go beyond feature-specific research and look at broader opportunities:
- Explore adjacent user problems
- Investigate **non-users** or **switchers** to competitors
- Use open-ended studies like: Site visits, Diary studies, Embedded observations (ride-alongs, usability shadows)

🧠 **Tip**: Use open framing like "Walk me through your process" or "Tell me about the last time you tried to..."

</details>

<details>
<summary>🫂 **5. Create a User-Focused Culture**</summary>

Drive customer obsession beyond your PM silo:
- Invite real users to team demos or AMAs
- Annotate mocks with real quotes ("This confused 4/5 users.")
- Include customer quotes in specs
- Gamify empathy (e.g., customer visit leaderboards)

📌 **Example:** Twilio has every employee — not just support — do customer support training to build empathy.

</details>

## 🪴 Growth Practices (How to Improve Over Time)

<details>
<summary>🧠 **1. Cultivate a Beginner's Mindset**</summary>

- Re-run onboarding flows as if you're a new user
- Ask recent users what confused them most
- Log your own initial confusion and friction

</details>

<details>
<summary>🔁 **2. Connect Product Choices to User Insights**</summary>

- Back each design, feature, and workflow with a real quote or research finding
- Use annotations: "This UI choice is due to 3/5 users failing the flow."

</details>

<details>
<summary>⚖️ **3. Prioritize Usability Issues Strategically**</summary>

Use a **frequency × impact** matrix:

| | Low Impact | High Impact |
|---|---|---|
| Low Frequency | Log it | Investigate |
| High Frequency | Deprioritize with note | Fix now |

📌 **Tip:** Log what you're **not fixing** with rationale — this shows strategic maturity.

</details>

<details>
<summary>🎯 **4. Surface the Key Insight That Unlocks the Problem**</summary>

> Like the "chalk mark on the generator," it's not about more feedback — it's about finding the one that changes the roadmap.

</details>

## 🧰 Useful Techniques & Questions

<details>
<summary>❓ **Questions to Dig Deeper with Users**</summary>

- "What happens before and after this task?"
- "How do you currently solve it?"
- "What's the hardest part?"
- "If we did this, what else would you need?"

</details>

<details>
<summary>🔗 **Jobs To Be Done (JTBD) Framework**</summary>

Users don't just use your product — they **hire it to do a job**.

🎯 **JTBD Examples:**
- "I use Google Calendar so I don't miss meetings."
- "I use Uber when I want to avoid parking stress."

🧠 **JTBD Questions:**
- "What goal were you trying to accomplish?"
- "What's frustrating about that today?"
- "What would a perfect version look like?"

📊 **Framework Table:**

| Component | Question | Example |
|-----------|----------|---------|
| Situation | When do they use it? | "When I'm planning a party" |
| Motivation | What do they want? | "I want to play upbeat music" |
| Outcome | What's the goal? | "So my friends have a good time" |

🔄 **Acronym**: **"SMO"** - Situation, Motivation, Outcome

🎯 **Mock Interview Question**: "How would you use JTBD to understand why users choose Spotify over Apple Music?"

</details>

<details>
<summary>🧭 **Customer Journey Mapping**</summary>

Understanding the user's **end-to-end lifecycle** helps uncover less visible pain points:

1. **Awareness** – Where/how do users first hear about you?
2. **Consideration** – What makes them explore options?
3. **Purchase** – What convinces them to activate/convert?
4. **Retention** – What habits or value loops keep them?
5. **Advocacy** – What triggers word-of-mouth loyalty?

📌 **Tip:** Use journey mapping exercises with sticky notes to align teams on user pain.

🔄 **Mnemonic**: **"ACPRA"** - Awareness, Consideration, Purchase, Retention, Advocacy

🎯 **Practice Question**: "Map the customer journey for someone discovering and adopting Notion for the first time."

</details>

<details>
<summary>📐 **Usability Guidelines – Nielsen's 10 Heuristics**</summary>

1. **Visibility of system status** - Show users what's happening through immediate feedback
2. **Match between system and real-world** - Use familiar language and concepts instead of technical jargon
3. **User control and freedom** - Provide clear exit points and undo/redo options for mistakes
4. **Consistency and standards** - Maintain uniform terminology and actions throughout the interface
5. **Error prevention** - Design interfaces that prevent problems before they occur
6. **Recognition rather than recall** - Make options visible so users don't have to remember information
7. **Flexibility and efficiency of use** - Offer shortcuts for experts while keeping the interface simple for beginners
8. **Aesthetic and minimalist design** - Present only relevant information to reduce clutter
9. **Help users recover from errors** - Use clear language to explain problems and suggest solutions
10. **Help and documentation** - Provide easily searchable, task-focused help when needed

📌 Use this as a **UX audit checklist** before launch.

</details>

<details>
<summary>🧪 **User Research Methods**</summary>

**Types of User Research:**

| Type | Description |
|------|-------------|
| User Interviews | Qualitative depth |
| Surveys | Quick signal from many users |
| Usability Tests | Watch behavior and friction |
| Field Studies | Observe environment/context |
| A/B Testing | Validate impact at scale |
| Diary Studies | Understand habits over time |
| Support Analysis | Spot repeat complaints |

**Research Mistakes to Avoid:**
- Asking leading questions ("Would you love X?")
- Talking more than listening
- Taking requests literally
- Doing research only at kickoff — do it continuously

</details>

<details>
<summary>🧠 **Memory Tip – "The 3 I's of User Insight"**</summary>

1. **Interview** – Talk to users directly
2. **Interpret** – Translate what they said into what they meant
3. **Improve** – Log and share findings; drive decisions

🔄 **Mnemonic**: **"III"** - Interview, Interpret, Improve

</details>

## 📌 Interview-Ready Takeaways

- Talk to users constantly — 5–10 per segment per project
- Go beyond requests — uncover root motivations using "Why-What-How"
- Validate fast with low-fidelity tools before major investments
- Use JTBD framework to understand true user motivations (SMO method)
- Map complete customer journey (ACPRA) to find hidden opportunities
- Apply Nielsen's 10 heuristics as UX audit checklist
- Follow the 3 I's: Interview, Interpret, Improve
- Evangelize insights org-wide to build user-centric culture

**CRITICAL INSTRUCTIONS FOR THIS CHAPTER:**

🚨 **ADAPTATION REQUIREMENTS:**
- **This example shows STYLE and DEPTH only - DO NOT copy this structure**
- **Adapt completely to YOUR chapter's unique content, headings, and frameworks**
- **Preserve the original organization and concepts from the source chapter**
- **Your chapter may have completely different sections - that's perfect!**

🎯 **STUDY-FOCUSED REQUIREMENTS:**
- **Digestible format**: Break dense content into bullet points, tables, or frameworks for easy consumption
- **Memory aids**: Create acronyms, mnemonics, or mental shortcuts for key frameworks and concepts
- **Practice elements**: Include mock interview questions and self-practice prompts where relevant
- **Natural definitions**: Provide clear, concise definitions without saying "one-line definition" - just state the definition naturally

**Critical Requirements:**
• Preserve ALL original headings, subheadings, and structural hierarchy from this specific chapter
• Extract EVERY framework, model, formula, definition, or method mentioned in this chapter
• Concisely summarize all examples, case studies, and practical applications from this chapter
• Capture every definition and key term exactly as written in this chapter
• Include ALL specific numbers, metrics, company names, and concrete details from this chapter
• Do NOT skip content from the end of chapters (common oversight)

**Notion Formatting Requirements:**
• Use **bold** for section titles with relevant emojis (adapt emojis to this chapter's content)
• Structure as **collapsible toggles** using `<details><summary>` tags for main sections
• Add nested bullet points and sub-details within each toggle for easy scanning
• Include code blocks for any frameworks/formulas specific to this chapter
• Use tables where appropriate for this chapter's content (especially for comparisons or processes)
• Include quote blocks for important principles from this chapter
• Add 🧠 **Memory Aid** or 🔄 **Mnemonic** sections to help with retention
• Include 🎯 **Practice Prompt** or **Mock Interview Question** where relevant
• Create clear visual hierarchy with proper nesting and indentation
• End with 📌 **Interview-Ready Takeaways** (concise bullet points summarizing key concepts)

**Output Quality Standards:**
• Zero hallucination - use only source material from this chapter
• Complete coverage - someone should ace interviews using only this summary
• Practical focus - emphasize actionable frameworks and techniques from this chapter
• Study-optimized depth - cover all concepts with appropriate detail for memorization
• Interview preparation - include practice questions and memory aids throughout
• Natural language - provide clean definitions and explanations without formulaic phrases
• **OUTPUT FORMAT**: Provide clean markdown without code block wrappers - ready for direct import to Notion
• Preserve the unique structure and concepts that make THIS chapter valuable

**Remember:** This is an individual chapter study guide for PM interview preparation. Adapt the formatting style to showcase THIS chapter's unique frameworks, examples, and structure while making it optimized for study and memorization.

Chapter: {chapter_title}

Chapter Content:
{chapter_content}"""

    return prompt
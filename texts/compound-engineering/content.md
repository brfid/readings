Source: https://every.to/guides/compound-engineering
Saved: 2026-04-19

# Compound Engineering

The core philosophy of compound engineering is that each unit of engineering work should make subsequent units easier—not harder.



 Most codebases get harder to work with over time because each feature you add injects more complexity. After 10 years, teams spend more time fighting their system than building on it because each new feature is a negotiation with the old ones. Over time, the codebase becomes harder to understand, harder to modify, and harder to trust.



 Compound engineering flips this on its head. Instead of features adding complexity and fragility, they teach the system new capabilities. Bug fixes eliminate entire categories of future bugs. When they are codified, patterns become tools for future work. Over time, the codebase becomes easier to understand, easier to modify, and easier to trust.

Every runs five products—[**Cora**](https://cora.computer/), [**Monologue**](https://www.monologue.to/), [**Sparkle**](https://makeitsparkle.co/), [**Spiral**](https://writewithspiral.com/), and our website [**Every.to**](http://Every.to)—with primarily single-person engineering teams. The system that makes this possible is a four-step loop that forms the basis of compound engineering:



 Plan → Work → Review → Compound → Repeat

The compound engineering workflow ships as a plugin. Install it, and the full system is ready to use.



 #### What's in the box

 - **[26 specialized agents.](https://github.com/EveryInc/compound-engineering-plugin/tree/main/agents)** Each agent is trained for a specific job.
 - **[23 workflow commands.](https://github.com/EveryInc/compound-engineering-plugin/tree/main/commands)** These include the main loop plus utilities.
 - **[13 skills.](https://github.com/EveryInc/compound-engineering-plugin/tree/main/skills)** These provide domain expertise, such as our agent-native architecture skill and style guide skill, on tap.

### [/workflows:brainstorm](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/brainstorm.md)
 When you're not sure what to build, start here.

 `/workflows:brainstorm Add user notifications`

 This command helps you brainstorm answers about what to build and plan answers for how to build them. Use this when requirements are fuzzy. The command runs lightweight repo research, then asks questions one at a time to clarify purpose, users, constraints, and edge cases. The AI then proposes approaches, and decisions are captured in `docs/brainstorms/` for handoff to `/workflows:plan`.


 ### [/workflows:plan](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/plan.md)
 Describe what you want and get back a plan for how to build it.

 `/workflows:plan Add email notifications when users receive new comments`

 This command spawns three parallel research agents: repo-research-analyst (codebase patterns), framework-docs-researcher (documentation), and best-practices-researcher (industry standards). Then the spec-flow-analyzer agent analyzes user flows and edge cases. Results are merged into a structured plan with affected files and implementation steps.



 Enable `ultrathink` mode (extended reasoning with deeper research) to automatically run [/deepen-plan](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/deepen-plan.md) after plan creation—this spawns over 40 parallel research agents.


 ### [/workflows:work](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/work.md)
 This is where the agent actually writes the code.

 `/workflows:work`

 Runs in four phases: quick start (creates a git worktree—an isolated copy of your repo for parallel work—and sets up branch), execute (implements each task with progress tracking), quality check (optionally spawns over five reviewer agents—Rails, TypeScript, security, performance), and ship it (runs linting, creates PR). Each phase has clear entry and exit criteria.


 ### [/workflows:review](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/review.md)
 Get your PR reviewed by a dozen specialized agents at once.

 `/workflows:review PR#123`

 Spawns more than 14 specialized agents in parallel that run simultaneously: security-sentinel, performance-oracle, data-integrity-guardian, architecture-strategist, pattern-recognition-specialist, code-simplicity-reviewer, and framework-specific reviewers (DHH-rails, Kieran-rails, TypeScript, Python). Everything gets combined into a single, prioritized list.


 #### Review agents
 The /review command spawns 14 specialized agents that analyze code in parallel. Each agent focuses on a specific domain and returns prioritized findings.

 Security


 - **security-sentinel** - Scans for top 10 vulnerabilities as defined by the Open Worldwide Application Security Project (OWASP), injection attacks, authentication flaws, and authorization bypasses

 Performance


 - **performance-oracle** - Detects N+1 queries, missing indexes, caching opportunities, and algorithmic bottlenecks

 Architecture


 - **architecture-strategist** - Evaluates system design decisions, component boundaries, and dependency directions
 - **pattern-recognition-specialist** - Identifies design patterns, anti-patterns, and code smells across the changeset

 Data


 - **data-integrity-guardian** - Validates migrations, transaction boundaries, and referential integrity
 - **data-migration-expert** - Checks ID mappings, rollback safety, and production data validation

 Quality


 - **code-simplicity-reviewer** - Enforces YAGNI, flags unnecessary complexity, and checks readability
 - **kieran-rails-reviewer** - Rails conventions, Turbo Streams patterns, model/controller responsibilities
 - **kieran-python-reviewer** - PEP 8 compliance, type hints, Pythonic idioms
 - **kieran-typescript-reviewer** - Type safety, modern ES patterns, clean architecture
 - **dhh-rails-reviewer** - 37signals conventions: simplicity over abstraction, Omakase stack

 Deployment


 - **deployment-verification-agent** - Generates pre-deploy checklists, post-deploy verification steps, and rollback plans

 Frontend


 - **julik-frontend-races-reviewer** - Detects race conditions in JavaScript and Stimulus controllers

 Agent-native


 - **agent-native-reviewer** - Ensures features are accessible to agents, not just humans


 #### Output format
 `P1 - CRITICAL (must fix):
[ ] SQL injection vulnerability in search query (security-sentinel)
[ ] Missing transaction around user creation (data-integrity-guardian)

P2 - IMPORTANT (should fix):
[ ] N+1 query in comments loading (performance-oracle)
[ ] Controller doing business logic (kieran-rails-reviewer)

P3 - MINOR (nice to fix):
[ ] Unused variable (code-simplicity-reviewer)
[ ] Could use guard clause (pattern-recognition-specialist)`

 #### Automated resolution

 The `/resolve_pr_parallel` command processes all findings automatically. P1 issues are fixed first, then P2s. Each fix runs in isolation so they don't step on each other, but you still manually review the generated fixes at the end.


 #### [/triage](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/triage.md)
 `/triage`

 This command presents each finding one by one for human decision: approve (add to to-do list), skip (delete), or customize (modify priority/details). Approved items get `status: ready` and can be worked on with `/resolve_todo_parallel`. Use this when you want to filter findings before committing to fixes.


 ### [/workflows:compound](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/compound.md)
 This command documents a solved problem for future reference.

 `/workflows:compound`

 This command spawns six parallel subagents: context analyzer (understands the problem), solution extractor (captures what worked), related docs finder (links to existing knowledge), prevention strategist (documents how to avoid recurrence), category classifier (tags for discovery), and documentation writer (formats the final doc). It creates a searchable markdown with YAML frontmatter that future sessions can find.


 ### [/lfg](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/lfg.md)
 With this command, you describe the feature, and the agent does the rest—planning, building, reviewing, and handing you a PR ready to merge.

 `/lfg Add dark mode toggle to settings page`

 This chains the full pipeline: plan → deepen-plan → work → review → resolve findings → browser tests → feature video → compound. It pauses for plan approval, then runs autonomously, and spawns more than 50 agents across all stages. With one command, you have a complete feature.

We have all been trained to believe certain things about software development. With improvements in AI tools, some of those beliefs are now obstacles. Here are eight of them to unlearn:


 ### 'The code must be written by hand'

 The actual requirement for you to do your job well as a software engineer is simply to write good code, which can be defined as maintainable code that solves the right problem. Who types—a human or an agent—doesn't matter.


 ### 'Every line must be manually reviewed'

 Again, a core requirement to be a good engineer is to write quality code. Manual line-by-line review is one method to get there, but so are automated systems that catch the same issues.



 One reason that developers still find themselves relying on manual review is that they don't trust the results. If you don't trust the results, fix the system, instead of compensating by doing everything yourself.


 ### 'Solutions must originate from the engineer'

 When AI can research approaches, analyze tradeoffs, and recommend options, the engineer's job becomes to add taste—knowing which solution fits this codebase, this team, and this context.


 ### 'Code is the primary artifact'

 A system that produces code is more valuable than any individual piece of code. A single brilliant implementation matters less than a process that consistently produces good implementations.


 ### 'Writing code is the core job function'

 A developer's job is ship value. Code is just one input in that job—planning, reviewing, and teaching the system all count too. Effective compound engineers write less code than before and ship more.


 ### 'First attempts should be good'

 In our experience, first attempts have a 95 percent garbage rate. Second attempts are still 50 percent. This isn't failure—it's the process.



 Expecting perfection on attempt one is like expecting a junior developer to nail a complex feature without context. So make it your goal to get it right the first time. Focus on iterating fast enough that your third attempt lands in less time than attempt one.


 ### 'Code is self-expression'

 Developers subconsciously see AI-assisted development as an attack on their identity. It feels like a blow to the ego.



 But the code was never really yours. It belongs to the team, the product, and the users. Letting go of code as self-expression is liberating. No attachment means you take feedback better, refactor without flinching, and skip the arguments about whether the code is good enough.


 ### 'More typing equals more learning'

 Many developers fear that by not typing it, they are not learning it. However, the reality is that understanding matters more than muscle memory today.



 You learn and build understanding by reviewing, by catching mistakes, and by knowing when the AI is wrong. The developer who reviews 10 AI implementations understands more patterns than the one who hand-typed two.


 ### Transition challenges
 **Less typing feels like less work.** It isn't. Directing an agent requires more thinking than implementation because you are spending less time on keystrokes and more time thinking about important decisions.

 **Letting go feels risky.** Autonomous execution—handing things over to agents—triggers anxiety in many developers. This fades once they recognize they're not ceding control. Instead, they're encoding it into constraints, conventions, and review processes that scale better than manual oversight.

 **Who built this?** Features shipping without directly writing the code can feel like cheating. But planning, reviewing, and ensuring quality standards is the work. You did the thinking. All the AI did was the writing.


 These reactions indicate a fundamental shift in how work gets done, and they're expected. By talking about them openly at Every, we hope to make it easier for others to speak about their experiences.

### Extract your taste into the system

 Every codebase reflects the taste of the developers who built it, from naming conventions to error handling patterns and testing approaches. That taste usually isn't documented anywhere. It lives in senior engineers' heads and is transferred through code review. This neither scales nor lets others on the team learn.



 The solution is to extract and document these choices. Write these preferences down in CLAUDE.md or AGENTS.md so the agent reads it every session. Build specialized agents for reviewing, testing, and deploying, as well as skills that reflect your taste. Add slash commands that encode your preferred approaches. Point the agent at your existing style guides, architecture docs, and decision records, which all include examples of the way that you like to build.



 Once the AI understands how you like to write code, it'll produce code you actually approve instead of code you have to fix.


 ### The 50/50 rule

 Previously, I suggested an 80/20 rule for building features: 80 percent of time planning and review, 20 percent on working and compounding. When you look at your broader responsibilities as a developer, you should allocate 50 percent of engineering time to building features, and 50 percent to improving the system—in other words, any work that helps build institutional knowledge rather than shipping something specific.



 In traditional engineering, teams put 90 percent of their time into features and 10 percent into everything else. Work that isn't a feature feels like a distraction—something you do when you have spare time, which you never do. But that \"everything else\" is what makes future features easier: things like creating review agents, documenting patterns, and building test generators. When you treat that work as overhead instead of an investment, the codebase accumulates debt.



 An hour spent creating a review agent saves 10 hours of review over the next year. You can spend time building a test generator that saves weeks of manual test writing. System improvements make work progressively faster and easier, but feature work doesn't.


 ### Trust the process, build safety nets

 AI assistance doesn't scale if every line requires human review. You need to trust the AI.



 Trust doesn't mean blind faith. It means setting up guardrails such as tests, automatic review, and monitoring that flag issues so you don't have to watch every step.



 When you feel as if you can't trust the output, don't compensate by switching to manually reviewing the code. Add a system that makes that step trustworthy, such as creating a review agent that flags issues.


 ### Make your environment agent-native

 If a developer can see or do something, the agent should be allowed to see or do it too.



 - Running tests
 - Checking production logs
 - Debugging with screenshots
 - Creating pull requests


 Anything that you don't let the agent handle, you have to do yourself manually. The goal should be full environmental parity between human and AI developers.


 ### Parallelization is your friend

 You used to be the bottleneck because human attention only allows one task at a time. The new bottleneck is compute—how many agents you can run at once.



 Run multiple agents and multiple features at the same time. Perform review, testing, and documentation all at once. When you are stuck on one task, start another, and let agents work while planning the next step.


 ### Plans are the new code

 The plan document is now the most important thing you produce. Instead of coding first and documenting later, as you might have traditionally, start with a plan. This becomes the source of truth your agents use to generate, test, and validate code.



 Having a plan helps capture decisions before they become bugs. Fixing ideas on paper is cheaper than fixing code later.


 ### Core principles

 In summary, the beliefs that underpin this new approach to software development are:



 - **Every unit of work makes subsequent work easier.** Code, documentation, and tooling should build on each other and make future work faster, not slower.
 - **Taste belongs in systems, not in review.** Bake your judgment into configuration, schemas, and automated checks. If you don't you'll be spending time manually checking, which does not scale.
 - **Teach the system, don't do the work yourself.** Time spent giving agents more context pays exponential dividends, but time spent typing code only solves the task in front of you.
 - **Build safety nets, not review processes.** The way to build trust in building with AI is by building verification infrastructure, not by gatekeeping manually at every step.
 - **Make environments agent-native.** Structure projects so AI agents can navigate and modify them autonomously.
 - **Apply compound thinking everywhere.** Every artifact—code, docs, tests, prompts—should enable the next iteration to move faster.
 - **Embrace the discomfort of letting go.** When you delegate to AI tools, you have to be okay with imperfect results that scale, rather than perfect results that don't.
 - **Ship more value. Type less code.** Your output should be measured by the number of problems solved, not the number of keystrokes you logged.


 The principles extend beyond engineering to design, research, or even writing—any discipline where codifying taste and context help make future work go faster and easier. The steps are the same: Plan, execute, review, compound.

The compound engineering loop—plan, work, review, compound—is the process. But how much of that process you allow the AI to own depends on where you are in your familiarity and aptitude with AI. There are five stages against which developers can plot themselves to understand where they sit.



 Most developers who struggle with AI-assisted development don't know where they are on this ladder. They hear about multi-agent review systems and parallel cloud execution, feel overwhelmed, and either give up or try to skip ahead. Skipping stages doesn't work because you will feel uncomfortable and distrustful of the tools. Each rung builds the mental models and habits required for the next. So slow down, figure out where you are, and focus on building from there.


 ### The stages

 #### Stage 0: Manual development

 At this stage, you are writing code line by line without any AI. You perform research via documentation and Stack Overflow. Your debugging process happens through code reading and print statements. Manual development built great software for decades, but sadly it's not fast enough in 2025.


 #### Stage 1: Chat-based assistance

 At this stage, you are using AI as a smart reference tool, querying ChatGPT, Claude, or Cursor, receiving code snippets, and copy-pasting what's useful. The AI accelerates your research and boilerplate generation, but you are still fully in control, reviewing every line.


 #### Stage 2: Agentic tools with line-by-line review

 At this stage, agentic tools—AI assistants that can read files and make changes directly—enter the workflow: Claude Code, Cursor Composer, and Copilot Chat. You allow the AI to read files and make changes directly in the codebase based on the context you have provided. You are a gatekeeper, approving or rejecting everything that the agent proposes, which is still a painstaking process.



 Most developers plateau here and don't get to enjoy the upside of handing more over to AI.


 #### Stage 3: Plan-first, PR-only review

 This is the stage where everything changes. You and AI collaborate on a detailed plan including requirements, approach, and edge cases. Then the developer steps away and allows the AI to implement the plan without supervision. The output is a pull request, which you then review. Finally, you are out of the line level of the code and can catch problems in the PR review instead of babysitting the AI while it builds.


 Compound engineering begins here as each cycle of planning, building, and reviewing teaches the system something that makes the next cycle easier and faster.

 #### Stage 4: Idea to PR (single machine)

 You provide an idea, and the agent handles everything: codebase research, planning, implementation, test execution, self-review, issue resolution, and PR creation. At this stage, your involvement shrinks to three steps: ideation, PR review, and merge. However, you are still running one thing at a time on your own computer.


 #### Stage 5: Parallel cloud execution (multiple devices)

 This is the final stage. You move execution to the cloud and run things in parallel. Because you're not tied to a laptop, you can direct your agents from anywhere—a coffee shop, a Panamanian beach, or your phone.



 You kick off three features, three agents work independently, and you review PRs as they finish. If you push it further, you allow agents to start monitoring feedback and proposing fixes without being asked. No longer an individual contributor are you. You're commanding a fleet.

Even if you don't have a fancy multi-agent review system at your fingertips, you can still get the benefits by asking these three questions before approving any AI output:



 - **"What was the hardest decision you made here?"** This forces the AI to reveal where the tricky parts are and where it had to make judgment calls.
 - **"What alternatives did you reject, and why?"** This shows you the options it considered and helps catch if it made a bad choice.
 - **"What are you least confident about?"** This gets the AI to admit where it might be wrong. LLMs know where their weaknesses are, but you have to ask.

Agent-native architecture means giving the agent the same capabilities you have. If the agent can't run tests, you have to run them. If it can't see logs, you have to debug. Every capability you withhold from the AI becomes a task you have to do yourself.


 ### The agent-native checklist
 To see if you are working in an agent-native way, check your agent's capabilities. Can your agent:

 #### Development environment

 - Run your application locally
 - Run your test suite
 - Run linters and type checkers
 - Run database migrations
 - Seed development data


 #### Git operations

 - Create branches
 - Make commits
 - Push to remote
 - Create pull requests
 - Read PR comments


 #### Debugging

 - View local logs
 - View production logs (read-only)
 - Take screenshots of the UI
 - Inspect network requests
 - Access error tracking (Sentry, etc.)


 ### Progressive agent-native
 You don't need to be 100 percent agent-native immediately. Give your agent or agents gradual access to an increasing number of things:



 Level 1: Basic development

 The agents have file access and can run tests and git commits. This is the basis to unlock basic compound engineering.

By default Claude Code asks for permission before every action such as creating a file as a safety measure. The `--dangerously-skip-permissions` flag turns those prompts off. The name is intentionally scary to make you think before using it. But for compound engineering at stage three or above, the constant requests for permission will kill your flow. Here are some guidelines for when to require the AI to ask for permission and when not:


 ### When to use it

 #### Use it when:

 - **You trust the process.** You have a good plan and good review systems.
 - **You're in a safe environment.** You're working in a sandbox where nothing you do will hurt real users or a live product.
 - **You want velocity.** The asks for permission slow down the workflow. Skip them to move fast.


 #### Don't use it when:

 - **You're learning.** The requests for permission from the AI help you understand what's happening.
 - **You're in production.** Never run with skip permissions when you're touching production code because that touches real users.
 - **You don't have good rollback.** If you can't easily undo mistakes, keep the prompts.


 ### How I use it
 I always run with skip permissions:

 `alias cc='claude --dangerously-skip-permissions'`


 I do this in a specific setup that helps avoid risk. I'm on my laptop, not a production server. I'm working in a branch that's completely separate from the main codebase. I have tests. I can revert anything. Real users will never see this code until I'm ready. The "dangerous" flag isn't actually dangerous here—it just helps me go faster.


 ### Safety without prompts
 If you're not using permission prompts, you need other safety mechanisms.



 Git is your safety net

 Everything the agent does is in git. `git reset --hard HEAD~1` and you're back.

Design is easier to iterate on in code than in mockups—you can click through it and feel the interactions. But you don't want to experiment in your production codebase. This section covers how to prototype designs in throwaway projects, test them with users, and capture your design taste so the AI can replicate it.


 ### The baby app approach

 Create a throwaway project—a "baby app"—where you can iterate freely without worrying about tests, architecture, or breaking anything. Once the design feels right, extract the patterns and bring them back to the real project.


 #### The workflow

 - **Create a prototype repo.** `mkdir baby-myapp && cd baby-myapp`
 - **Vibe code the design.** "Create a settings page with dark mode toggle. Make it look modern."
 - **Iterate until it looks right.** "More spacing. Toggle more prominent. Inline, not stacked."
 - **Capture the design system.** Once you have something you are pleased with, extract colors, spacing, typography, and component patterns.
 - **Transfer to main app.** Use the prototype as reference when building the real feature.


 ### UX discovery loop
 When you don't know what to build, vibe coding is great for exploring:


 - Generate multiple versions. Tell the agent to come up with five different versions of the settings page and see what it comes up with.
 - Click through each one. Use them and see what feels right.
 - Share with users. Show them the prototype and ask: "Would this flow confuse you?"
 - Collect feedback on functional prototypes. Unlike a Figma mockup, they can actually click around.
 - **Delete everything and start over with a proper plan.** The prototype is for learning only, not shipping.


 ### Working with designers

 #### Traditional flow
 Collaboration between designers and developers usually looks like this: The designer creates a mockup. The developer interprets it and builds something. The designer says, "That's not quite right." Back and forth until it eventually matches—maybe.

 #### Compound flow
 With compound engineering, the back-and-forth shrinks.


 - The designer creates a mockup in Figma
 - You run [/plan](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/plan.md) with Figma link and tell the AI to implement it exactly.
 - The AI builds it.
 - The [figma-design-sync](https://github.com/EveryInc/compound-engineering-plugin/blob/main/agents/design/figma-design-sync.md) agent checks if the implementation matches the mockup.
 - The designer reviews the live version, not a screenshot.
 - Iterate until it's perfect.


 ### Codifying design taste
 Once you've worked with a designer on a few features, you'll notice patterns such as their preferred colors and how they like forms laid out. Write those down in a skill file. Using this, the AI can now produce designs that match the designer's taste—even when the designer isn't involved.

 `# skill: our-design-system

## Colors
- Primary: #4F46E5
- Background: #F9FAFB

## Spacing
- Use 4px base unit
- Sections: 32px gap

## Patterns
- Buttons: 12px horizontal padding
- Cards: subtle shadows, not borders
- Forms: single-column, max-width 400px`

 ### Design agents


 [design-iterator](https://github.com/EveryInc/compound-engineering-plugin/blob/main/agents/design/design-iterator.md)

 Takes a screenshot of the current design, analyzes what's not working, makes improvements, and repeats. Each pass refines the design further.

Vibe coding is for people who don't care about the code itself—they want results.



 Maybe you're a product manager prototyping ideas. Maybe you're a designer testing how an interaction feels. Maybe you're building a personal project, and you'll never look at the code anyway. You just want to make sure the thing works—this is the vibe coder's philosophy.


 ### The vibe coder's philosophy

 This section is about skipping the ladder and going straight to stage four, where you describe what you want and let the agents build it.


 ### The fast path
 Skip the ladder. Go straight to Stage 4.



 -
 **Describe what you want**
 `[/lfg](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/lfg.md) Create a web app that lets me track my daily habits with checkboxes`

 -
 **Wait**
 The agent figures out what to build, creates the code, runs tests, reviews itself, makes a PR.


 -
 **Check if it works**
 If yes, done. If no, say what's wrong. Let the agent fix it.

When the AI handles implementation, the team dynamics shift. You need new agreements: who approves plans, who owns PRs, and what humans should review when agents have done the first pass.


 ### The new team dynamics

 **Traditional:** In a traditional setting, developers collaborate in the following way: Person A writes code → Person B reviews → Discussion in PR comments → Merge after approval



 **Compound:** In a compound engineering setting, developers collaborate as follows: Person A creates plan → AI implements → AI agents review → Person B reviews the AI review → Merge after human approval


 ### Team standards



 #### Plan approval

 Reading a plan and agreeing with it is a decision. Silence is not approval—it's the absence of a decision.



 **Standard:** The standard should require explicit sign-off before implementation, whether that's a comment, a tag in the commit message, or some other approval marker.

Structure research so AI can use it. Build persona documents, link insights to features, close the loop between research and implementation.


 ### The research-development gap

 **Traditional:** In traditional software development, user researchers and developer collaboration looks like this: Researcher conducts interviews → Writes report → Report sits in Google Drive → Developer builds feature → Developer never reads report → Feature doesn't match user needs



 **Compound:** In compound engineering, that collaboration looks like this: Research generates structured insights → Insights become planning context → AI references insights when planning → Features are informed by research → Usage data validates insights → Insights compound


 ### Structuring research
 Raw interview notes are hard for AI to use. Structure them:

 `# research/interviews/user-123.md
---
participant: Marketing Manager, B2B SaaS
date: 2025-01-15
focus: Dashboard usage patterns
---

## Key Insights

### Insight: Morning dashboard ritual
**Quote**: "First thing every morning, I check for red flags."
**Implication**: Dashboard needs to surface problems quickly.
**Confidence** (4/5 participants)`

 ### Building persona documents
 Create persona documents that the AI can reference:

 `# personas/marketing-manager.md

## Goals
1. Prove marketing ROI to leadership
2. Identify underperforming campaigns quickly

## Frustrations
1. Too much data, hard to find what matters
2. Exporting for reports is tedious

## Quotes
- "I need to see problems, not everything."
- "My boss wants a PDF, not a link."`

 ### Research-informed planning
 `[/workflows:plan](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/plan.md) Add export scheduling

Research context:
- 3/5 interviewed users mentioned exporting weekly
- The marketing-manager persona exports every Friday
- Current pain: manual export process

Design for: Automated weekly exports to email`



 More coming soon

 Research compound loop, AI-assisted analysis, documentation standards.

Your users are already telling you what to build through how they use your product. Each click is a clue. You just have to pay attention.


 ### Pattern types to look for


 Heavy usage patterns

 These are features that are used way more than expected. Another signal could be users returning to the same page repeatedly.

Most teams treat copy as an afterthought—something to fill in after the feature is built. But copy is part of the user experience. It deserves the same attention as the code.


 ### Copy is part of the plan
 Include copy in your plans from the start, codify your voice so the AI can follow it, and review it like you'd review any other output:

 `## Feature: Password Reset Flow

### User-Facing Copy
- Email subject: "Reset your password"
- Success message: "Check your email. We sent a reset link."
- Error (not found): "We couldn't find an account with that email.
 Want to create one instead?"`
 Now when the AI implements, the copy is already there.

 ### Codify your voice
 Create a skill that defines your copy voice, such as the following:

 `# skill: our-copy-voice

## Principles
1. Talk to users like humans, not robots
2. Error messages should help, not blame
3. Short sentences. Clear words.

## Words to avoid
- "Invalid" → "didn't work"
- "Error" → describe what happened
- "Successfully" → just say what happened
- "Please" → just ask directly

## Examples
Bad: "Invalid credentials. Please try again."
Good: "That password isn't right. Try again or reset it."`

 ### Review copy like code
 Add copy review to your [/workflows:review](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/workflows/review.md) process:


 copy-reviewer agent


 - **Clarity:** Can a non-technical user understand this?
 - **Helpfulness:** Does this help the user succeed?
 - **Tone:** Does this match our voice guide?
 - **Consistency:** Does this match similar text elsewhere?

Congratulations, you've shipped something. Now it's time to tell the world. The same system that builds features can announce them. Generate release notes from plans, create social posts, and capture screenshots automatically.


 ### The compound flow

 - An engineer creates a plan that includes the product value proposition.
 - The AI implements a feature.
 - The AI generates release notes from the plan.
 - The AI generates social posts from the release notes.
 - The AI generates screenshots using Playwright.
 - The engineer reviews and ships everything together.

 It all flows from one place. No one has to hand anything off, and nothing slips through the cracks.

 ### Generating release notes
 After implementing a feature:

 `Based on the plan and implementation for [feature], write release notes:
1. Lead with the user benefit (what can they do now?)
2. Include one concrete example
3. Mention any breaking changes
4. Keep it under 200 words`
 The AI has the plan, the code changes, and the tests. It knows exactly what was built.

 ### Generating changelogs
 For multiple features, use [/changelog](https://github.com/EveryInc/compound-engineering-plugin/blob/main/commands/changelog.md):

 `/changelog`
 Looks at recent merges to main, reads the plans/PRs for each, generates an engaging changelog.

 ### Automated screenshots
 Use Playwright to capture screenshots for marketing:

 `Take screenshots showing the new notification settings:
1. The settings page with notifications section
2. An example notification email
3. The in-app notification badge`
 No more asking engineering for screenshots, and no more out-of-date screenshots.



 More coming soon

 Marketing voice skill, feature announcement flow, and metrics that compound.

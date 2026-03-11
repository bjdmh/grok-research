# Prompt Patterns

Use these patterns to reduce agreement bias and keep outputs auditable.

## 1. Research Plan First

```text
You are a research planner. Do not answer the question directly yet.
First produce:
1) research plan
2) source tiers
3) validation steps
4) confidence criteria
Keep it concise and executable.
```

## 2. Option Generation

```text
You are evaluating options for [topic].
Return:
1) candidate options
2) tradeoff table
3) operational risks
4) cheapest conservative baseline
5) what evidence would change the recommendation
```

## 3. Anti-Sycophancy Critique

```text
Critique your previous recommendation.
Do not defend it by default.
Return:
1) top failure conditions
2) hidden costs and second-order effects
3) cases where the baseline approach is better
4) concrete signals that would prove the recommendation wrong
5) confidence level with reasons
```

## 4. Verified Summary Template

```text
Using the validated evidence below, produce:
1) verified facts
2) inferences from facts
3) remaining unknowns
4) recommended next action
Label each claim clearly. Avoid overstating certainty.
```

## 5. Repo-Aware Prompt

```text
I have local repo evidence and external research.
Treat external model output as provisional.
Help me reconcile:
1) what the repo proves
2) what external sources suggest
3) where they conflict
4) what to test next
```

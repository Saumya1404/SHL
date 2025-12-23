import json
from app.services.intent_service import Intent
from app.core.llm_client import call_llm
import logging
import re


LLM_PROMPT = """
#### ROLE:
You are an expert taxonomy and signal-classification specialist for a recruitment
assessment recommendation system.

You are a CLASSIFIER, not a decision-maker.

Your job is to extract, normalize, and strictly categorize skills and signals
from the user query so that downstream deterministic logic can rank assessments correctly.

#### SYSTEM CONTEXT (READ CAREFULLY):

The system already uses deterministic logic to extract:
- duration constraints
- obvious skills
- basic intent flags

You MUST NOT:
- contradict existing extracted fields
- re-infer numeric constraints
- rank or recommend assessments
- invent skills not implied by the query

You MUST:
- strictly classify skills into correct categories
- remove generic or misleading terms from technical skill lists
- normalize skills into canonical forms

#### EXISTING PARSED INTENT (READ-ONLY — DO NOT MODIFY):

{intent}

#### USER QUERY:

{query}

## YOUR TASK

Analyze the USER QUERY together with the EXISTING PARSED INTENT and output
ONLY the missing or refined classification signals.

Your responsibilities:

1. Identify **core technical skills** that are mandatory for the role.
2. Identify **supporting technical skills** that help but are not sufficient alone.
3. Identify **generic role terms** that should NOT be treated as skills.
4. Identify additional **behavioral skills**, if any.
5. Infer **seniority** and **role type** only if clearly implied.
6. Classify keyword importance to guide retrieval bias (qualitative only).

## CRITICAL SKILL CLASSIFICATION RULES (STRICT)

### 1. core_technical_skills
Hard, role-defining skills without which the candidate is NOT qualified.

Include ONLY:
- programming languages
- frameworks
- platforms
- tools
- technologies

Examples:
- "Java", "Python", "Spring", "React", "AWS", "SQL"

Rules:
- Programming languages are ALWAYS core technical skills.
- If removing the skill makes the role invalid, it is core.
- Do NOT include generic words like “developer” or “IT”.

### 2. supporting_technical_skills
Technical concepts that support the role but are NOT sufficient alone.

Examples:
- "System Design", "APIs", "Microservices", "Databases"

Rules:
- These must NOT be used for hard filtering.
- They may assist ranking but cannot dominate it.

### 3. generic_role_terms
Broad descriptors that apply to many unrelated jobs and must NOT be treated as skills.

Examples:
- "Developer", "Engineer", "IT", "Professional", "Software Role"

Rules:
- These MUST NOT appear in technical skill lists.
- These terms are ignored in ranking and filtering.

### 4. behavioral_skills
Soft skills, collaboration traits, communication, leadership, or interpersonal abilities.

Examples:
- "Collaboration", "Communication", "Stakeholder Management"

## SENIORITY CLASSIFICATION

Infer ONLY if clearly implied.

Allowed values:
- "junior"
- "mid"
- "senior"
- "executive"

Rules:
- Explicit words like “Senior”, “Lead”, “Principal” → senior
- Otherwise return null

## ROLE TYPE CLASSIFICATION

Infer ONLY if clearly implied.

Allowed values:
- "IC" (Individual Contributor)
- "manager"
- "executive"
- "consultant"

Rules:
- If the role emphasizes hands-on development → IC
- If people management is explicit → manager
- Otherwise return null

## KEYWORD IMPORTANCE (QUALITATIVE ONLY)

Classify the importance of keywords found in the query.

Allowed values:
- "critical" → core hiring requirement
- "context" → important but secondary
- "default" → background signal

Rules:
- Do NOT assign numeric weights.
- Do NOT rank keywords.
- Include only meaningful keywords from the query.

## OUTPUT RULES (MANDATORY)

- Output MUST be valid JSON.
- Output MUST NOT include markdown, comments, or explanations.
- Use lowercase for all skill strings.
- Deduplicate all lists.
- If uncertain, return an empty list or null.
- Do NOT repeat fields already present unless refining them.

## JSON OUTPUT FORMAT (STRICT)

{{
  "core_technical_skills": ["string"],
  "supporting_technical_skills": ["string"],
  "generic_role_terms": ["string"],
  "additional_behavioral_skills": ["string"],
  "seniority": "string" or null,
  "role_type": "string" or null,
  "keyword_importance": {{
    "keyword": "critical | context | default"
  }}
}}

"""


def enrich_with_llm(intent:Intent, query:str)->Intent:
    prompt = LLM_PROMPT.format(query=query,intent = intent)
    try:
        raw = call_llm(prompt)
        print("LLM raw repr:", repr(raw), "type:", type(raw))
        cleaned_json = raw.strip()
        pattern = r"^```(?:json)?\s*(.*?)\s*```$"
        match = re.search(pattern, cleaned_json, re.DOTALL)
        
        if match:
            cleaned_json = match.group(1)
        data = json.loads(cleaned_json)
    except Exception:
        logging.exception("LLM call or JSON parse failed")
        return intent
    
    if 'additional_technical_skills' in data:
        intent.technical_skills.extend(s for s in data['additional_technical_skills'] if s not in intent.technical_skills)
    if 'additional_behavioral_skills' in data:
        intent.behavioral_skills.extend(s for s in data['additional_behavioral_skills'] if s not in intent.behavioral_skills)

    if 'seniority' in data and intent.seniority is None:
        intent.seniority = data['seniority']
    if 'role_type' in data and intent.role_type is None:
        intent.role_type = data['role_type']

    if data.get('additional_technical_skills'):
        intent.technical_confidence = min(1.0, intent.technical_confidence + 0.1)
    if data.get('additional_behavioral_skills'):
        intent.behavioral_confidence = min(1.0, intent.behavioral_confidence + 0.1)

    if 'keyword_importance' in data:
        intent.keyword_importance = data['keyword_importance']
    if 'core_technical_skills' in data:
        intent.core_technical_skills = data['core_technical_skills']
    if 'supporting_technical_skills' in data:
        intent.supporting_technical_skills = data['supporting_technical_skills']
    if 'generic_role_terms' in data:
        intent.generic_role_terms = data['generic_role_terms']


    intent.needs_balance = (
        intent.technical_confidence >= 0.5
        and intent.behavioral_confidence >= 0.5
    )
    return intent




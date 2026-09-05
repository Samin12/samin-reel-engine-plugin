#!/usr/bin/env python3
"""Portable Hold Your Voice helpers.

This script intentionally has no third-party dependencies. It is not the Hold
Your Voice product backend; it is the reusable local layer for Codex projects:
build a sample-grounded profile, scan for AI cadence, and generate line-level
rewrite prompts.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


TEXT_EXTENSIONS = {
    ".md",
    ".mdx",
    ".txt",
    ".html",
    ".htm",
    ".rst",
    ".adoc",
    ".csv",
}

AI_PATTERN_RULES = [
    # --- Binary reframing & negation ---
    ("binary_reframing", re.compile(
        r"\b(?:it'?s|that'?s|this\s+(?:is|was)|here'?s)\s+not\b.{0,80}\b(?:it'?s|that'?s|but)\b|"
        r"\b(?:the\s+)?(?:hard\s+)?(?:part|point)\s+isn'?t\b.{0,80}\b(?:it'?s|but)\b|"
        r"\byou\s+don'?t\s+need\b.{0,80}\byou\s+need\b|"
        r"\b(?:brand|trust|strategy|marketing|pricing|success|growth|content|design)\s+is\s+not\s+(?:just\s+)?about\b",
        re.I,
    )),
    ("not_just_but", re.compile(
        r"\bnot\s+just\b.{3,80}\bbut\s+(?:also\s+)?|"
        r"\bnot\s+only\b.{3,80}\bbut\s+(?:also\s+)?",
        re.I,
    )),
    ("more_than_just", re.compile(
        r"\bmore\s+than\s+just\b|\bit'?s\s+not\s+just\s+about\b",
        re.I,
    )),

    # --- Truth/reality posturing ---
    ("truth_harsh_reality", re.compile(
        r"\b(?:the\s+)?(?:uncomfortable|hard|harsh|brutal|ugly|unsexy|real|honest)\s+(?:truth|reality)\b|"
        r"\bthe\s+truth\s+is\b|\bthe\s+reality\s+is\b|\bhere'?s\s+the\s+truth\b|"
        r"\bthe\s+ugly\s+truth\b|\bthe\s+harsh\s+reality\b|"
        r"\b(?:brutal\s+honesty|real\s+talk)\b|\breality\s+check:",
        re.I,
    )),

    # --- Staccato drama & performance cadence ---
    ("staccato_drama", re.compile(
        r"\b(?:no|not)\s+\w[^.!?\n]{0,40}[.!?]\s*(?:no|not)\s+\w[^.!?\n]{0,40}[.!?]\s*(?:no|not|just)\s+\w",
        re.I,
    )),
    ("founder_cadence", re.compile(
        r"\b(?:the\s+)?moment\b.{3,80}\bbecomes?\b|"
        r"\b(?:here'?s|here\s+is)\s+(?:the\s+)?(?:thing|kicker|part\s+most\s+people\s+miss|what\s+nobody'?s\s+saying)\b|"
        r"\b(?:and|but)\s+honestly\?|\bhere'?s\s+the\s+kicker\b|"
        r"\bwhat\s+nobody'?s\s+(?:saying|talking\s+about)\b|"
        r"\bthe\s+part\s+most\s+people\s+miss\b|"
        r"\bthe\s+best\s+part\?|\bthe\s+kicker\?|"
        r"\bsame\s+[^.!?\n]{1,35}[.!?]\s*(?:better|nicer|cleaner|calmer|safer)\s+[^.!?\n]{1,35}[.!?]?",
        re.I,
    )),
    ("restatement_polish", re.compile(
        r"\bwhich\s+is\s+another\s+way\s+of\s+saying\b|"
        r"\bin\s+other\s+words\b|"
        r"\bto\s+put\s+it\s+(?:simply|another\s+way)\b|"
        r"\bin\s+a\s+nutshell\b",
        re.I,
    )),
    ("spoiler_reveal", re.compile(
        r"\bspoiler(?:\s+alert)?:\s*it'?s\s+not\b|"
        r"\b(?:and|but)\s+here'?s\s+the\s+(?:truth|reality)\b",
        re.I,
    )),

    # --- Landscape / era / temporal grandstanding ---
    ("landscape_era", re.compile(
        r"\b(?:in\s+)?(?:today'?s\s+)?(?:fast.paced|ever.evolving|ever.changing|digital)\s+(?:world|age|era|landscape)\b|"
        r"\b(?:ever.evolving|ever.increasing|constantly\s+growing|increasingly)\s+(?:landscape|world)\b|"
        r"\bin\s+today'?s\s+world\b|\bin\s+the\s+digital\s+age\b|"
        r"\bin\s+this\s+era\s+of\b|"
        r"\bnow\s+more\s+than\s+ever\b|"
        r"\b(?:as|like)\s+never\s+before\b|"
        r"\bhas\s+never\s+been\s+more\s+important\b|"
        r"\bthe\s+rise\s+of\s+(?:the\s+)?\w+\b|"
        r"\b(?:a|the)\s+new\s+era\s+of\b|"
        r"\b(?:has\s+been\s+around\s+for\s+centuries|since\s+the\s+dawn\s+of\s+time)\b",
        re.I,
    )),

    # --- Formulaic connectors & transitions ---
    ("formulaic_connector", re.compile(
        r"\b(?:firstly|secondly|thirdly|lastly|moreover|furthermore|in\s+addition\b(?:\s*,\s*|$)|"
        r"in\s+conclusion|to\s+summarize|to\s+sum\s+up|to\s+recap|in\s+summary\b(?:\s*,\s*|$)|"
        r"it\s+is\s+important\s+to\s+note|it'?s\s+important\s+to\s+note|it\s+should\s+be\s+noted|"
        r"it'?s\s+worth\s+noting\s+that|it'?s\s+important\s+to\s+remember\b|"
        r"however\s*,\s*it'?s\s+important\s+to\s+remember|"
        r"keep\s+in\s+mind\s+that|remember\s+that\b|"
        r"on\s+top\s+of\s+that\b)",
        re.I,
    )),

    # --- Transitions: balance & contrast ---
    ("balanced_contrast", re.compile(
        r"\bon\s+the\s+one\s+hand\b|"
        r"\bon\s+the\s+other\s+hand\b|"
        r"\bon\s+the\s+surface\b.{0,80}\b(?:but\s+)?beneath\b|"
        r"\bat\s+first\s+glance\b|"
        r"\bon\s+the\s+flip\s+side\b|"
        r"\bat\s+first\s*,\s*it\s+might\s+seem\b|"
        r"\bon\s+paper\b.{0,80}\bin\s+practice\b|"
        r"\bwhether\s+you\s+(?:love\s+it\s+or\s+hate\s+it|realize\s+it\s+or\s+not)\b|"
        r"\blike\s+it\s+or\s+not\b|"
        r"\bready\s+or\s+not\b",
        re.I,
    )),

    # --- Hedging & non-committal ---
    ("hedging_noncommittal", re.compile(
        r"\bit\s+depends\b.{0,60}\bbut\b|"
        r"\bno\s+one.size.fits.all\b|"
        r"\btailor\s+(?:it|this|these|them)\b.{0,40}\bto\s+(?:your|the)\s+(?:needs|context|audience)\b|"
        r"\balways\s+tailor\b|"
        r"\b(?:in\s+many\s+ways|from\s+a\s+broader\s+perspective)\b|"
        r"\bin\s+the\s+context\s+of\b|"
        r"\b(?:chances\s+are|more\s+often\s+than\s+not|at\s+first\s*,\s*it\s+might\s+seem)\b|"
        r"\bit\s+can\s+be\s+tempting\s+to\b|\byou\s+might\s+be\s+tempted\s+to\b|"
        r"\bonly\s+time\s+will\s+tell\b|"
        r"\bboth\s+sides\s+have\s+valid\s+points\b|"
        r"\bthat\s+said\b",
        re.I,
    )),

    # --- Let's/X invitation ---
    ("lets_invitation", re.compile(
        r"\blet'?s\s+(?:dive|explore|break\s+(?:it|this)\s+down|delve|be\s+honest)\b|"
        r"\b(?:dive|delv(?:e|ing))\s+(?:deeper|into|the\s+intricacies)\b|"
        r"\bdeep\s+dive\b|\blet'?s\s+dive\s+in\b",
        re.I,
    )),

    # --- Empathy/validation openers ---
    ("empathy_opener", re.compile(
        r"\bit'?s\s+easy\s+to\s+feel\b|\byou'?re\s+not\s+alone\b|"
        r"\bif\s+you'?ve\s+ever\s+felt\b|\byou'?re\s+not\s+imagining\s+it\b|"
        r"\byou'?re\s+not\s+wrong\s+to\s+feel\b|"
        r"\byou\s+deserve\b|\bfear\s+not\b|"
        r"\bshouting\s+into\s+the\s+void\b|"
        r"\bcurious\s+what\s+others\s+think\b",
        re.I,
    )),

    # --- Journey / destination clichés ---
    ("journey_cliche", re.compile(
        r"\b(?:brand|learning|success|life|growth|writing|fitness|business)\s+isn'?t\s+a\s+destination\b.{0,40}\bjourney\b|"
        r"\bit'?s\s+a\s+journey\b.{0,50}\bnot\s+a\s+destination\b|"
        r"\bno\s+matter\s+where\s+you\s+are\s+on\s+your\s+journey\b|"
        r"\bembark\s+on\s+(?:a|your|the|this)\b|"
        r"\byou'?re\s+still\s+early\b|\bit'?s\s+still\s+day\s+one\b|"
        r"\bfrom\s+(?:confusion\s+to\s+clarity|followers\s+to\s+fans|ideas\s+to\s+income)\b|"
        r"\b(?:brand.building|writing|creative|learning)\s+journey\b",
        re.I,
    )),

    # --- Marketing/inflated verbs ---
    ("inflated_verbs", re.compile(
        r"\b(?:unlock|harness|leverage)\s+the\s+power\s+of\b|"
        r"\b(?:unlock|unleash)\s+(?:the\s+)?(?:potential|power)\b|"
        r"\b(?:supercharge|turbocharge|revolutionize\s+the\s+way)\b|"
        r"\b(?:transform|elevate|enhance|boost|improve)\s+your\s+\w+\b|"
        r"\btake\s+(?:your|it|this|them|their)\b.{0,30}\bto\s+(?:the\s+next\s+level|new\s+heights)\b|"
        r"\b(?:game.changer|on\s+steroids)\b|"
        r"\bmaster\s+the\s+art\s+of\b|"
        r"\bdiscover\s+a\s+powerful\s+way\b",
        re.I,
    )),

    # --- Metaphor clusters ---
    ("ai_metaphors", re.compile(
        r"\b(?:beacon|lighthouse)\s+(?:of|for|in)\b|"
        r"\b(?:tapestry|symphony|tides)\s+of\b|"
        r"\b(?:flood|avalanche|tsunami)\s+of\b|"
        r"\b(?:noise|signal)\b.{0,30}\b(?:signal|noise)\b|"
        r"\b(?:north\s+star|double.edged\s+sword|blessing\s+and\s+a\s+curse)\b|"
        r"\b(?:silent\s+killer|hidden\s+gem|hidden\s+lever|low.hanging\s+fruit)\b|"
        r"\b(?:tip\s+of\s+the\s+iceberg|scratch(?:es)?\s+the\s+surface)\b|"
        r"\b(?:skeleton|framework|scaffolding|blueprint|roadmap|playbook)\b\s+(?:for|to|that|as)\b|"
        r"\b(?:wealth\s+of|treasure\s+trove)\b|"
        r"\b(?:the\s+)?power\s+of\b.{0,40}\b(?:cannot|should\s+not|is\s+immense|is\s+real|is\s+undeniable)\b",
        re.I,
    )),

    # --- Inflated importance claims ---
    ("inflated_importance", re.compile(
        r"\b(?:crucial|critical|pivotal)\s+role\b|"
        r"\b(?:a\s+testament\s+to|the\s+results\s+speak\s+for\s+themselves)\b|"
        r"\b(?:remarkably|incredibly|highly)\s+\w+\b|"
        r"\b(?:significant\s+milestone|at\s+scale)\b|"
        r"\b(?:at\s+its\s+finest|at\s+the\s+heart\s+of)\b|"
        r"\b(?:the\s+power\s+of\b.{0,40}\b(?:cannot|should\s+not)\b)|"
        r"\b(?:championing|advocating\s+for)\b.{0,40}\b(?:change|reform|transparency)\b",
        re.I,
    )),

    # --- Audience-inclusion triads ---
    ("audience_triad", re.compile(
        r"\bwhether\s+you'?re\s+(?:a\s+)?\w+(?:\s+\w+)?\s*,\s*(?:a\s+)?\w+(?:\s+\w+)?\s*,\s*(?:or|and)\s+(?:a\s+)?\w+\b|"
        r"\bfrom\s+(?:solo\s+)?(?:tiny\s+)?\w+\s+to\s+(?:large\s+)?(?:global\s+)?\w+\s*,\s*everyone\s+\w+\b|"
        r"\bwhether\s+you'?re\s+(?:a\s+)?beginner\b|"
        r"\bno\s+matter\s+where\s+you\s+are\b",
        re.I,
    )),

    # --- SEO / guide framing ---
    ("guide_framing", re.compile(
        r"\byou'?re\s+in\s+the\s+right\s+place\b|"
        r"\bhere'?s\s+a\s+step.by.step\s+guide\b|"
        r"\b(?:step\s+1|step\s+2|step\s+3)\b|"
        r"\b(?:first\s*,\s*second\s*,\s*third)\b|"
        r"\bkey\s+(?:takeaways?|insights?)\b|"
        r"\bactionable\s+tips?\b|"
        r"\bno\s+fluff\b|\bno.nonsense\b",
        re.I,
    )),

    # --- Wrapping/closing patterns ---
    ("wrapping_patterns", re.compile(
        r"\b(?:ultimately|at\s+the\s+end\s+of\s+the\s+day|the\s+bottom\s+line\s+is|"
        r"it\s+all\s+comes\s+down\s+to)\b|"
        r"\b(?:best.case\s+scenario|worst.case\s+scenario)\b|"
        r"\b(?:the\s+good\s+news\s+is|the\s+bad\s+news\s+is)\b|"
        r"\blet\s+that\s+sink\s+in\b|\bif\s+you\s+think\s+about\s+it\b|"
        r"\bthe\s+stakes\s+are\s+high\b|"
        r"\b(?:before\s+you\s+know\s+it|in\s+the\s+blink\s+of\s+an\s+eye)\b|"
        r"\b(?:more\s+often\s+than\s+you\s+think|you\s+won'?t\s+believe)\b|"
        r"\b(?:happens|occur|churn|happen|changes?)\s+(?:faster|quicker|sooner)\s+than\s+you\s+think\b",
        re.I,
    )),

    # --- Temporal / trend clichés ---
    ("trend_cliches", re.compile(
        r"\b(?:attention|trust|retention|data)\s+is\s+the\s+new\s+(?:currency|growth\s+hack|acquisition|oil)\b|"
        r"\bthe\s+best\s+time\s+(?:to\s+\w+|was)\b.{0,80}\b(?:second.best|is\s+now)\b|"
        r"\b(?:low\s+barrier|high\s+leverage)\b|"
        r"\b(?:quick\s+wins?|silver\s+bullet)\b|"
        r"\bstart\s+small\s+and\s+iterate\b|"
        r"\b(?:from\s+\w+\s+to\s+\w+\s*[,:]\s*)\b",
        re.I,
    )),

    # --- Pain points & problem framing ---
    ("pain_points_framing", re.compile(
        r"\bpain\s+points?\b(?!\s+of)|\baddress\s+(?:the|their|your)\s+pain\s+points\b|"
        r"\bspeak\s+(?:directly\s+)?to\s+(?:their|your)\s+pain\s+points\b",
        re.I,
    )),

    # --- Overly structured / meta patterns ---
    ("meta_structuring", re.compile(
        r"\b(?:in\s+this\s+(?:article|guide|post|piece)|this\s+(?:article|guide|post|piece)\s+(?:explores|will\s+explore|discusses))\b|"
        r"\b(?:this\s+essay\s+will\s+discuss|in\s+conclusion\s*,\s*this\s+essay)\b|"
        r"\blet\s+me\s+know\s+if\s+you\s+need\s+(?:any|more)\s+help\b|"
        r"\bfeel\s+free\s+to\s+ask\b|"
        r"\b(?:if\s+you\s+have\s+follow.up\s+questions|i'?m\s+here\s+to\s+help)\b",
        re.I,
    )),

    # --- Experience / friction words ---
    ("ux_buzzwords", re.compile(
        r"\b(?:seamless(?:\s+experience|\s+journey)?|frictionless(?:\s+journey|\s+experience)?|"
        r"holistic\b(?:\s+\w+)?|comprehensive\b(?:\s+\w+)?|innovative\b(?:\s+\w+)?|"
        r"cutting.edge|state.of.the.art|"
        r"robust(?:\s+\w+)?|scalable(?:\s+\w+)?|best.in.class)\b",
        re.I,
    )),

    # --- Story / narrative templates ---
    ("story_templates", re.compile(
        r"\b(?:little\s+did\s+(?:i|we)\s+know|"
        r"at\s+first\s*,\s*i\s+was\s+skeptical\b.{0,80}\bbut\b|"
        r"imagine\s+this|picture\s+this|"
        r"you\s+wake\s+up\s+to\b)",
        re.I,
    )),

    # --- Specifically AI-vocab density words ---
    ("ai_vocab_density", re.compile(
        r"\b(?:delve|underscore|testament|intricate|multifaceted|cornerstone|landscape|"
        r"foster|harness|tapestry|illuminate|pivotal|elevate|empower|"
        r"seamlessly|revolutionize|supercharge|transformative|holistic|comprehensive|"
        r"innovative|impactful|meaningful|utilize|paradigm|navigate|endeavor|realm|"
        r"profound|encapsulate|synergy|robust|facilitate|bolster|streamline|"
        r"differentiate|myriad|transform|vibrant|dynamic|bustling|ecosystem|"
        r"ever.increasing|constantly\s+growing|increasingly|"
        r"unlock|unleash|(?:re)?imagin(?:e|ing)|curate|iterate|optimize|"
        r"amplify|align|drive\s+\w+|foster|cultivate|shed\s+light\s+on|"
        r"quietly|silently|behind\s+every\b|"
        r"not\s+all\s+\w+\s+are\s+created\s+equal|"
        r"there'?s\s+a\s+fine\s+line\s+between|"
        r"the\s+line\s+between\b.{0,40}\bis\s+blurry\b|"
        r"you\s+don'?t\s+have\s+to\b.{0,40}\b(?:to|you\s+can)\b|"
        r"champion(?:ing|s|ed)\b|advocat(?:ing|e[ds]?)\s+for\b|"
        r"more\s+often\s+than\s+you\s+think\b)",
        re.I,
    )),

    # --- Em dash (typographic tell) ---
    ("em_dash", re.compile(r"\u2014")),

    # --- Buyer psychology templates ---
    ("buyer_psychology", re.compile(
        r"\bpeople\s+don'?t\s+(?:just\s+)?buy\b.{0,60}\bthey\s+buy\b|"
        r"\bpeople\s+buy\s+the\s+feeling\b|"
        r"\bpeople\s+don'?t\s+read\b.{0,40}\bthey\s+skim\b|"
        r"\b(?:it'?s\s+not\s+about|people\s+don'?t\s+care\s+about)\s+your\s+product\b",
        re.I,
    )),

    # --- The X of Y metaphoric positioning ---
    ("x_of_y_metaphor", re.compile(
        r"\bthe\s+(?:netflix|uber|airbnb|apple|google|spotify|tesla|amazon)\s+of\s+\w+\b|"
        r"\boperating\s+system\s+(?:of|for)\s+(?:your|the)\s+\w+\b",
        re.I,
    )),

    # --- Overwhelm-reassurance ---
    ("overwhelm_reassurance", re.compile(
        r"\b(?:can\s+feel|might\s+seem|can\s+be)\s+overwhelming\b.{0,80}\bbut\s+it\s+doesn'?t\s+have\s+to\s+be\b|"
        r"\b(?:can\s+feel|might\s+seem)\s+(?:intimidating|complex|difficult)\b.{0,80}\bbut\b",
        re.I,
    )),

    # --- Pros/cons framing ---
    ("pros_cons_framing", re.compile(
        r"\b(?:pros\s+and\s+cons|advantages\s+and\s+disadvantages)\s+(?:of|to)\b|"
        r"\bhere\s+are\s+the\s+pros\s+and\s+cons\b",
        re.I,
    )),

    # --- Triple-adjective bloat ---
    ("triple_adjective", re.compile(
        r"\b(?:\w+,\s+\w+,\s+(?:and\s+)?\w+\s+(?:approach|strategy|solution|framework|platform|system|tool|method|plan|process))\b|"
        r"\b(?:simple|clear|easy)\s*,\s*(?:useful|effective|powerful|intuitive)\s*,\s*(?:and\s+)?(?:memorable|sustainable|scalable|actionable)\b",
        re.I,
    )),

    # --- Behind-the-scenes / hidden depth ---
    ("hidden_depth", re.compile(
        r"\bbehind\s+(?:the\s+scenes|every\s+\w+)\b.{0,80}\b(?:lies|is)\b|"
        r"\bbehind\s+the\s+scenes\b|"
        r"\bbeneath\s+the\s+surface\b",
        re.I,
    )),

    # --- Self-referential / AI disclaimer ---
    ("self_referential", re.compile(
        r"\bas\s+an\s+ai\s+(?:language\s+)?model\b|"
        r"\bi\s+(?:can'?t|cannot)\s+provide\s+(?:legal|medical|financial|investment)\s+advice\b|"
        r"\bi\s+don'?t\s+have\s+(?:personal\s+experiences|feelings|opinions)\b",
        re.I,
    )),

    # --- Placeholder brackets ---
    ("placeholder_brackets", re.compile(
        r"\[(?:your\s+(?:brand|product|company|list|audience|name|metric|goal)|"
        r"insert\s+(?:metric|name|number|value|example)|target\s+\w+)\]",
        re.I,
    )),

    # --- Zoom / camera metaphor ---
    ("zoom_camera", re.compile(
        r"\b(?:zooming\s+(?:in|out)|from\s+a\s+broader\s+perspective|let'?s\s+zoom\s+(?:in|out))\b",
        re.I,
    )),

    # --- Core/essence statements (#41, #130) ---
    ("essence_statements", re.compile(
        r"\bat\s+(?:its|the)\s+(?:core|heart)\b|"
        r"\bat\s+(?:its|the)\s+(?:core|heart)\s*(?:of\s+)?\w+\s+(?:is|lies|are)\b",
        re.I,
    )),

    # --- Analogy / simile invitations (#42-43) ---
    ("ai_analogies", re.compile(
        r"\bthink\s+of\b.{0,30}\bas\s+(?:a|the|your)\b|"
        r"\b(?:your|the|a|an|\w+)\s+(?:is|are)\s+(?:like|kind\s+of\s+like)\s+(?:a|the)\b|"
        r"\bimagine\s+(?:your|the|a|an|\w+)\s+as\b",
        re.I,
    )),

    # --- "Sounds simple but" (#44) and "In fact" (#46) ---
    ("simple_but_infact", re.compile(
        r"\b(?:this|it|that)\s+(?:might|may|can)\s+sound\s+simple\s*[,.]?\s+but\b|"
        r"\b(?:sounds?\s+simple\s*[,.]?\s+but)\b|"
        r"\bin\s+fact\s*,\s*\w+",
        re.I,
    )),

    # --- "The X you didn't know you needed" (#71) ---
    ("clickbait_didnt_know", re.compile(
        r"\bthe\s+\w+(?:\s+\w+)?\s+you\s+didn'?t\s+know\s+you\s+needed\b",
        re.I,
    )),

    # --- Self-referential restatement (#79) ---
    ("self_referential_restatement", re.compile(
        r"\byou\s+(?:asked|wanted\s+to\s+know|wonder(?:ing)?)\s+(?:how|what|why|whether)\b.{0,80}\b(?:let'?s|so|here'?s)\b|"
        r"\byou\s+(?:asked|wanted\s+to\s+know)\s+about\b.{0,80}\b(?:let'?s|so|here'?s)\s+(?:break|walk|dive|explore)\b",
        re.I,
    )),
]

ABSTRACT_STYLE_WORDS = {
    "alignment",
    "authenticity",
    "awareness",
    "clarity",
    "confidence",
    "consistency",
    "differentiation",
    "execution",
    "framework",
    "identity",
    "messaging",
    "narrative",
    "personality",
    "positioning",
    "preference",
    "presence",
    "recall",
    "relevance",
    "resonance",
    "signal",
    "strategy",
    "trust",
    "utility",
    "value",
    # Expanded from 220 AI patterns document
    "ecosystem",
    "landscape",
    "space",
    "realm",
    "sphere",
    "paradigm",
    "synergy",
    "holistic",
    "robust",
    "scalable",
    "innovative",
    "transformative",
    "comprehensive",
    "sustainable",
    "impactful",
    "meaningful",
    "actionable",
    "seamless",
    "frictionless",
    "cutting-edge",
    "state-of-the-art",
    "best-in-class",
    "optimization",
    "efficiency",
    "productivity",
    "growth",
    "retention",
    "acquisition",
    "engagement",
    "conversion",
    "monetization",
    "scalability",
    "agility",
    "resilience",
    "empowerment",
    "transformation",
    "innovation",
    "disruption",
    "evolution",
    "revolution",
    "iteration",
    "velocity",
    "leverage",
    "amplification",
    "acceleration",
    "facilitation",
    "orchestration",
    "curation",
    "personalization",
    "customization",
    "democratization",
    "accessibility",
    "inclusivity",
    "infrastructure",
    "architecture",
    "foundation",
    "cornerstone",
    "pillar",
    "backbone",
    "lifeblood",
    "catalyst",
    "enabler",
    "driver",
    "engine",
    "flywheel",
    "moat",
    "advantage",
    "differentiator",
    "proposition",
    "promise",
    "mission",
    "vision",
    "purpose",
    "intention",
    "mindset",
    "mindfulness",
    "consciousness",
    "feedback",
    "vulnerability",
    "transparency",
    "accountability",
    "responsibility",
    "ownership",
    "agency",
    "autonomy",
    "sovereignty",
    "freedom",
    "liberation",
    "elevation",
    "ascension",
    "mastery",
    "excellence",
    "greatness",
    "potential",
    "possibility",
    "opportunity",
    "abundance",
    "prosperity",
    "fulfillment",
    "happiness",
    "wellness",
    "wellbeing",
    "balance",
    "harmony",
    "coherence",
    "congruence",
    "integrity",
    "honor",
    "dignity",
    "respect",
    "empathy",
    "compassion",
    "humanity",
    "connection",
    "belonging",
    "tribe",
    "movement",
    "renaissance",
    "awakening",
    "enlightenment",
    "breakthrough",
    "tipping point",
    "inflection",
    "pivot",
    "shift",
    "transition",
    "metamorphosis",
    "rebirth",
    "reinvention",
}

GENERIC_OPENERS = re.compile(
    r"^(?:most|many|some|all)\s+(?:brands|teams|people|founders|companies|businesses|organizations|leaders)\b|"
    r"^(?:in\s+)?(?:today'?s|the)\s+(?:fast.paced|ever.evolving|modern|digital|current|contemporary)\s+(?:world|age|era|landscape|economy)\b",
    re.I,
)
QUESTION_OPENER = re.compile(
    r"^(?:have you|do you|did you|what if|why do|how do|are you|is your|can you|will you)\b",
    re.I,
)
LESSON_OPENER = re.compile(
    r"^(?:the most important thing|the key to|success is|if you want to|what i learned|"
    r"the hard part|the point isn'?t|you don'?t need|the hard(?:est)?\s+(?:part|thing))\b",
    re.I,
)

# CTA/engagement bait endings
CTA_ENDINGS = re.compile(
    r"\blet\s+me\s+know\s+if\s+you\s+need\s+(?:any\s+more\s+|any\s+|more\s+)?help\b|"
    r"\bfeel\s+free\s+to\s+(?:ask|reach\s+out|contact|dm|let\s+me\s+know)\b|"
    r"\bcurious\s+what\s+others\s+think\b|"
    r"\bi'?m\s+here\s+to\s+help\b|"
    r"\bif\s+you\s+have\s+follow.up\s+questions\b",
    re.I,
)

SEVEN_WORD_SENTENCE_PATTERN = re.compile(
    r"^(?:\w+\s+){6}(?:\w+)[.!?]$",
)


def strip_markup(text: str, suffix: str = "") -> str:
    if suffix.lower() not in {".html", ".htm"}:
        return text
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return html.unescape(text)


def read_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    return strip_markup(raw, path.suffix)


def iter_text_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        path = Path(raw).expanduser()
        if not path.exists():
            raise SystemExit(f"path not found: {path}")
        if path.is_file():
            files.append(path)
            continue
        for item in sorted(path.rglob("*")):
            if not item.is_file():
                continue
            if any(part.startswith(".") for part in item.relative_to(path).parts):
                continue
            if item.suffix.lower() in TEXT_EXTENSIONS:
                files.append(item)
    return files


def words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9']*", text)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
    return [part.strip() for part in parts if words(part)]


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if len(words(p)) >= 6]


def variance_label(lengths: list[int]) -> str:
    if len(lengths) < 3:
        return "medium"
    mean = sum(lengths) / len(lengths)
    if mean <= 0:
        return "medium"
    stdev = math.sqrt(sum((length - mean) ** 2 for length in lengths) / len(lengths))
    ratio = stdev / mean
    if ratio < 0.35:
        return "low"
    if ratio > 0.85:
        return "high"
    return "medium"


def infer_case_style(lines: list[str]) -> str:
    starters = []
    properish = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        match = re.search(r"[A-Za-z]", stripped)
        if not match:
            continue
        char = match.group(0)
        starters.append(char)
        if re.search(r"\b[A-Z][a-z]{2,}\b", stripped):
            properish += 1
    if not starters:
        return "mixed"
    lower_ratio = sum(1 for char in starters if char.islower()) / len(starters)
    if lower_ratio >= 0.85 and properish <= len(starters) * 0.2:
        return "mostly lowercase"
    if lower_ratio <= 0.25:
        return "standard sentence case"
    return "mixed"


def infer_argument_pattern(text: str) -> str:
    low = text.lower()
    sentence_list = sentences(text)
    if not sentence_list:
        return "mixed"
    question_ratio = sum(1 for sentence in sentence_list if sentence.rstrip().endswith("?")) / len(sentence_list)
    first_person = len(re.findall(r"\b(?:i|we|my|our|me|us)\b", low))
    contrast = len(re.findall(r"\b(?:but|actually|instead|not|wrong|real|because)\b", low))
    numbers = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", low))
    if question_ratio > 0.18:
        return "question-led"
    if numbers >= max(4, len(sentence_list) // 10):
        return "data-led"
    if first_person >= max(6, len(sentence_list) // 4):
        return "narrative"
    if contrast >= max(8, len(sentence_list) // 3):
        return "contrarian"
    return "mixed"


def first_words(text: str, count: int = 7) -> str:
    found = words(text.lower())
    return " ".join(found[:count])


def top_opening_moves(paragraph_list: list[str], limit: int = 8) -> list[str]:
    counts: dict[str, int] = {}
    order: list[str] = []
    for paragraph in paragraph_list:
        move = first_words(paragraph, 6)
        if len(move.split()) < 3:
            continue
        if move not in counts:
            order.append(move)
        counts[move] = counts.get(move, 0) + 1
    ranked = sorted(order, key=lambda item: (-counts[item], order.index(item)))
    return ranked[:limit]


def choose_anchors(paragraph_list: list[str], limit: int = 3) -> list[str]:
    candidates = []
    for paragraph in paragraph_list:
        compact = re.sub(r"\s+", " ", paragraph).strip()
        if 80 <= len(compact) <= 420:
            candidates.append(compact)
    if not candidates:
        candidates = [re.sub(r"\s+", " ", p).strip()[:360] for p in paragraph_list if p.strip()]
    anchors: list[str] = []
    seen = set()
    for candidate in candidates:
        key = candidate[:80].lower()
        if key in seen:
            continue
        seen.add(key)
        anchors.append(candidate[:360])
        if len(anchors) >= limit:
            break
    return anchors


def build_profile(paths: list[str], name: str) -> dict[str, Any]:
    files = iter_text_files(paths)
    samples = []
    combined_parts = []
    for path in files:
        text = read_text(path).strip()
        if not text:
            continue
        samples.append({"path": str(path), "text": text})
        combined_parts.append(text)

    if not samples:
        raise SystemExit("no readable text samples found")

    combined = "\n\n".join(combined_parts)
    sentence_list = sentences(combined)
    paragraph_list = paragraphs(combined)
    sentence_lengths = [len(words(sentence)) for sentence in sentence_list if words(sentence)]
    paragraph_sentence_counts = [max(1, len(sentences(paragraph))) for paragraph in paragraph_list]
    line_list = [line for text in combined_parts for line in text.splitlines()]
    avg_sentence = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0
    avg_paragraph = round(sum(paragraph_sentence_counts) / len(paragraph_sentence_counts), 1) if paragraph_sentence_counts else 0
    opening_moves = top_opening_moves(paragraph_list)
    case_style = infer_case_style(line_list)
    argument_pattern = infer_argument_pattern(combined)
    anchors = choose_anchors(paragraph_list)

    cadence = [
        f"average sentence length around {avg_sentence} words",
        f"sentence length variance is {variance_label(sentence_lengths)}",
        f"average paragraph length around {avg_paragraph} sentences",
    ]
    if case_style == "mostly lowercase":
        cadence.append("leans lowercase in visible prose")

    never_list = [
        "here's the thing",
        "let's be honest",
        "at the end of the day",
        "not just x but y",
        "which is another way of saying",
        "in other words",
        "the moment x becomes y",
        "same x. better y.",
    ]

    voice_rules = [
        "trust the supplied samples over generic style advice",
        "open from a concrete observation, scene, mechanism, or quoted line",
        "keep the writer's natural sentence and paragraph rhythm",
        "preserve specific roughness when it carries the voice",
        "repair AI-pattern drift line by line instead of rewriting clean prose",
    ]
    if opening_moves:
        voice_rules.append("study these sample opening moves before drafting: " + "; ".join(opening_moves[:4]))

    return {
        "profile_version": "hold-your-voice-portable-v1",
        "name": name,
        "source_count": len(samples),
        "sources": [{"path": sample["path"], "chars": len(sample["text"])} for sample in samples],
        "word_count": len(words(combined)),
        "sentence": {"avg_words": avg_sentence, "variance": variance_label(sentence_lengths)},
        "paragraph": {"avg_sentences": avg_paragraph},
        "signature": {
            "case_style": case_style,
            "argument_pattern": argument_pattern,
            "opening_moves": opening_moves,
            "cadence": cadence,
            "anchors": anchors,
            "never_list": never_list,
        },
        "voice_rules": voice_rules,
        "ai_eliminator": {
            "rewrite_scope": "flagged-lines-only",
            "preserve_surrounding_lines": True,
            "avoid_polished_founder_cadence": True,
        },
    }


def line_style_hits(line: str) -> list[dict[str, str]]:
    low = (line or "").strip().lower()
    if not low:
        return []
    hits = []
    line_words = re.findall(r"[a-z']+", low)
    abstract_count = sum(1 for word in line_words if word in ABSTRACT_STYLE_WORDS)
    if abstract_count >= 3 and not re.search(r"\b(?:for example|for instance|such as)\b|\d", low):
        hits.append({"rule": "abstract_noun_cluster", "phrase": line.strip()[:160]})
    if GENERIC_OPENERS.match(low):
        hits.append({"rule": "generic_opening_generalization", "phrase": line.strip()[:160]})
    if QUESTION_OPENER.match(low):
        hits.append({"rule": "voice_question_opener", "phrase": "opens with a question instead of a concrete observation"})
    if LESSON_OPENER.match(low):
        hits.append({"rule": "voice_lesson_opener", "phrase": "opens with a lesson or inspirational claim"})
    if CTA_ENDINGS.search(low):
        hits.append({"rule": "cta_ending", "phrase": line.strip()[:160]})
    # detect TED-talk contrastive slogan pattern: "It's not X, it's Y" in a single line
    if re.search(r"\bit'?s\s+not\b.{0,40}\bit'?s\b", low):
        hits.append({"rule": "ted_talk_slogan", "phrase": line.strip()[:160]})
    # detect perfect 6-8 word marketing sentence that starts generic + has buzzword density
    line_parts = re.split(r"(?<=[.!?])\s+", line.strip())
    for part in line_parts:
        wc = len(re.findall(r"[a-zA-Z']+", part))
        if 6 <= wc <= 8 and part and part[-1] in ".!?":
            part_low = part.lower()
            generic_start = re.match(r"^(?:the|your|this|a|an|it|our|most|many|some|all)", part_low)
            has_buzzword = bool(re.search(r"\b(?:attention|trust|retention|brand|growth|strategy|content|value|customer|product|data)\b", part_low))
            if generic_start and has_buzzword:
                hits.append({"rule": "perfect_marketing_sentence", "phrase": part.strip()[:160]})
                break
    return hits


def _structural_analysis(text: str) -> list[dict[str, Any]]:
    """Analyze structural/rhythmic properties beyond individual word patterns."""
    hits: list[dict[str, Any]] = []
    sentence_list = sentences(text)
    paragraph_list = paragraphs(text)

    if not sentence_list:
        return hits

    # --- Burstiness (sentence length variance) ---
    lengths = [len(words(s)) for s in sentence_list if words(s)]
    if len(lengths) >= 5:
        mean = sum(lengths) / len(lengths)
        stdev = math.sqrt(sum((l - mean) ** 2 for l in lengths) / len(lengths))
        cv = stdev / mean if mean > 0 else 0
        if cv < 0.35:
            hits.append({
                "rule": "low_burstiness",
                "phrase": f"sentence length variation {cv:.2f} (< 0.35 = AI-flat rhythm)",
                "line": 0,
            })

    # --- Mechanical paragraph structure ---
    if len(paragraph_list) >= 3:
        para_sent_counts = [max(1, len(sentences(p))) for p in paragraph_list]
        para_mean = sum(para_sent_counts) / len(para_sent_counts)
        if para_mean > 0:
            para_stdev = math.sqrt(sum((c - para_mean) ** 2 for c in para_sent_counts) / len(para_sent_counts))
            para_cv = para_stdev / para_mean
            if para_cv < 0.30:
                hits.append({
                    "rule": "mechanical_paragraphs",
                    "phrase": f"paragraphs all similar length (cv={para_cv:.2f}, mean={para_mean:.1f} sentences)",
                    "line": 0,
                })

    # --- Over-structured lists: every list has exactly 3 items? ---
    list_item_pattern = re.compile(r"^[\s]*[-*•]\s+", re.M)
    list_items = list_item_pattern.findall(text or "")
    if len(list_items) >= 6:
        line_num = (text or "").split("\n").index([l for l in (text or "").split("\n") if list_item_pattern.match(l)][0]) + 1 if text else 0
        # check if list items follow a strict "X, Y, and Z" triad pattern
        triad_count = sum(1 for p in paragraph_list if len(sentences(p)) == 1 and len(re.findall(r"[-*•]", p)) >= 2)
        if triad_count >= 2:
            hits.append({
                "rule": "over_structured_lists",
                "phrase": "lists follow rigid 3-item pattern throughout",
                "line": line_num,
            })

    # --- Uniform sentence rhythm within paragraphs ---
    ai_rhythm_count = 0
    for para in paragraph_list:
        para_sentences = sentences(para)
        if len(para_sentences) >= 3:
            s_lengths = [len(words(s)) for s in para_sentences if words(s)]
            if s_lengths and all(12 <= l <= 22 for l in s_lengths):
                ai_rhythm_count += 1
    if ai_rhythm_count >= max(1, len(paragraph_list) * 0.6) and len(paragraph_list) >= 2:
        hits.append({
            "rule": "uniform_paragraph_rhythm",
            "phrase": f"{ai_rhythm_count}/{len(paragraph_list)} paragraphs have mechanical 12-22 word sentence uniformity",
            "line": 0,
        })

    # --- Formal/tone analysis: contractions ratio ---
    contraction_pattern = re.compile(r"\b(?:don'?t|can'?t|won'?t|isn'?t|aren'?t|wasn'?t|weren'?t|"
                                      r"hasn'?t|haven'?t|hadn'?t|shouldn'?t|wouldn'?t|couldn'?t|"
                                      r"mightn'?t|mustn'?t|it'?s|that'?s|what'?s|there'?s|"
                                      r"here'?s|who'?s|let'?s|i'?m|you'?re|we'?re|they'?re|"
                                      r"i'?ve|you'?ve|we'?ve|they'?ve|i'?ll|you'?ll|we'?ll|they'?ll)\b", re.I)
    contractions = len(contraction_pattern.findall(text or ""))
    total_words = len(words(text or ""))
    contraction_ratio = contractions / max(1, total_words / 100)  # per 100 words
    if total_words > 200 and contraction_ratio < 0.8:
        hits.append({
            "rule": "low_contractions",
            "phrase": f"{contraction_ratio:.1f} contractions per 100 words (human average 1.5-3.0; overly formal/rigid)",
            "line": 0,
        })

    # --- Overly formal hedging density ---
    formal_hedges_pattern = re.compile(
        r"\b(?:it\s+is\s+important\s+to\s+note|it\s+should\s+be\s+noted|it\s+is\s+worth\s+noting|"
        r"it\s+is\s+crucial\s+to|it\s+is\s+essential\s+to|it\s+appears\s+that|"
        r"there\s+is\s+a\s+possibility\s+that|one\s+should\s+consider|"
        r"it\s+is\s+imperative\s+to|it\s+is\s+necessary\s+to)\b",
        re.I,
    )
    formal_hedges = len(formal_hedges_pattern.findall(text or ""))
    if formal_hedges >= 2:
        hits.append({
            "rule": "formal_hedging_density",
            "phrase": f"{formal_hedges} formal hedging phrases found (institutional/overly polite tone)",
            "line": 0,
        })

    # --- Non-specific intensifiers density ---
    intensifiers_pattern = re.compile(
        r"\b(?:remarkably|incredibly|amazingly|extraordinarily|exceptionally|"
        r"tremendously|absolutely|completely|thoroughly|utterly)\s+\w+\b",
        re.I,
    )
    intensifiers = len(intensifiers_pattern.findall(text or ""))
    if intensifiers >= 3:
        hits.append({
            "rule": "generic_intensifiers",
            "phrase": f"{intensifiers} generic intensifiers (remarkably/incredibly/amazingly) - marketing tone",
            "line": 0,
        })

    # --- Perfect grammar / no fragments ---
    total_sentences = len(sentence_list)
    fragments = sum(1 for s in sentence_list if len(words(s)) <= 4 and s.strip() and s.strip()[-1] in ".!?"
                    and not re.search(r"\b(?:yes|no|hey|hi|ok|bye|wow|oh)\b", s.lower()))
    fragment_ratio = fragments / max(1, total_sentences)
    if total_sentences > 20 and fragment_ratio < 0.02:
        hits.append({
            "rule": "no_fragments",
            "phrase": f"only {fragments} sentence fragments in {total_sentences} sentences - over-polished",
            "line": 0,
        })

    return hits


def scan_text(text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for rule_id, pattern in AI_PATTERN_RULES:
        for match in pattern.finditer(text or ""):
            snippet = match.group(0).strip()
            if not snippet:
                continue
            line_no = text[: match.start()].count("\n") + 1
            hits.append({"line": line_no, "rule": rule_id, "phrase": snippet[:160]})

    for line_no, line in enumerate((text or "").splitlines(), 1):
        for hit in line_style_hits(line):
            hits.append({"line": line_no, "rule": hit["rule"], "phrase": hit["phrase"], "text": line.strip()[:240]})

    # Structural / rhythmic analysis
    for structural_hit in _structural_analysis(text):
        hits.append(structural_hit)

    # Staccato triplet detection — only fire when sentences are clearly performative
    sentence_hits = []
    for line_no, line in enumerate((text or "").splitlines(), 1):
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            found = words(sentence)
            if found:
                sentence_hits.append((line_no, sentence.strip(), len(found)))
    for idx in range(len(sentence_hits) - 2):
        window = sentence_hits[idx : idx + 3]
        lengths_ok = all(count <= 5 for _, _, count in window)
        if not lengths_ok:
            continue
        combined = " ".join(s[1] for s in window).lower()
        connector_words = {"but", "and", "or", "so", "because", "then", "if", "when", "while"}
        has_connector = any(f" {w} " in f" {combined} " for w in connector_words)
        # Allow: pure performance staccato (3 verbs in a row, no connectors, no "I")
        pure_staccato = all(count <= 3 for _, _, count in window) and not has_connector
        has_i = bool(re.search(r"\b(?:i|we|my|our|me|us)\b", combined))
        if pure_staccato or (not has_connector and not has_i):
            hits.append(
                {
                    "line": window[0][0],
                    "rule": "voice_staccato_triplet",
                    "phrase": "three short sentences in a row reads like performance",
                    "text": window[0][1],
                }
            )
            break

    return sorted(hits, key=lambda item: (item.get("line", 0), item.get("rule", "")))


def format_scan_text(path: str, text: str, hits: list[dict[str, Any]]) -> str:
    if not hits:
        return f"{path}: no deterministic AI-pattern issues found"
    lines = [f"{path}: {len(hits)} issue(s)"]
    for hit in hits:
        phrase = hit.get("phrase", "")
        lines.append(f"- line {hit.get('line')}: {hit.get('rule')} - {phrase}")
    return "\n".join(lines)


def load_draft(path: str) -> tuple[str, str]:
    if path == "-":
        return "stdin", sys.stdin.read()
    draft_path = Path(path).expanduser()
    if not draft_path.exists():
        raise SystemExit(f"draft not found: {draft_path}")
    return str(draft_path), read_text(draft_path)


def build_rewrite_prompt(draft_name: str, draft: str, profile_text: str | None, constraints: str = "", meta: dict[str, Any] | None = None) -> str:
    hits = scan_text(draft)
    if meta:
        hits = filter_hits_by_weights(hits, meta)
    issue_lines = "\n".join(
        f"- line {hit['line']} [{hit['rule']}]: {hit.get('phrase', '')}"
        for hit in hits
    ) or "- none found by deterministic scan"

    numbered_draft = "\n".join(f"{idx}: {line}" for idx, line in enumerate(draft.splitlines(), 1))
    profile_block = profile_text.strip() if profile_text and profile_text.strip() else "(no voice profile supplied)"
    constraints_block = constraints.strip() if constraints.strip() else "(none)"

    return f"""Rewrite only the flagged lines. Do not rewrite the whole piece.

Return only valid JSON in this exact shape:
{{"replacements":[{{"line":1,"text":"replacement line"}}]}}

Rules:
- Include only flagged line numbers.
- Preserve unflagged lines exactly by not returning them.
- Preserve the original argument and local meaning.
- Use the voice profile as the benchmark when present.
- Remove AI cadence, polished founder cadence, abstract strategy-deck language, and generic lesson shapes.
- Do not add new sections, hooks, CTAs, markdown, bullets, or commentary.

Voice profile:
{profile_block}

Extra constraints:
{constraints_block}

Flagged lines:
{issue_lines}

Draft with line numbers ({draft_name}):
{numbered_draft}
"""


DEFAULT_NEVER_LIST = [
    "here's the thing",
    "let's be honest",
    "at the end of the day",
    "not just x but y",
    "which is another way of saying",
    "in other words",
    "the moment x becomes y",
    "same x. better y.",
]

SIGNAL_VERSION = "hold-your-voice-signal-v1"
META_SIGNAL_VERSION = "hold-your-voice-signal-v2"

PATTERN_CONFIDENCE_THRESHOLD = 0.30  # patterns below this are auto-suppressed
PATTERN_STATUS = ("active", "declining", "stale")


def lines_changed_pct(orig_line: str, acc_line: str) -> bool:
    """return True if two lines differ meaningfully as edited text."""
    return orig_line.strip() != acc_line.strip()


def build_signal_report(
    original_path: str,
    accepted_path: str,
    original_text: str,
    accepted_text: str,
    profile: dict[str, Any] | None,
) -> dict[str, Any]:
    """diff original vs accepted to extract learning signals."""
    orig_lines = original_text.splitlines(keepends=True)
    acc_lines = accepted_text.splitlines(keepends=True)
    orig_hits = scan_text(original_text)

    flagged_line_nums: set[int] = set(hit["line"] for hit in orig_hits)
    # build a map: line_num -> [pattern_ids]
    line_pattern_map: dict[int, list[str]] = {}
    for hit in orig_hits:
        line_pattern_map.setdefault(hit["line"], []).append(hit["rule"])

    patterns_accepted: dict[str, int] = {}
    patterns_overridden: dict[str, int] = {}
    changed_unflagged: dict[int, str] = {}

    min_lines = min(len(orig_lines), len(acc_lines))

    for i in range(min_lines):
        line_no = i + 1
        changed = lines_changed_pct(orig_lines[i], acc_lines[i])
        patterns = line_pattern_map.get(line_no, [])

        if changed and patterns:
            for pid in patterns:
                patterns_accepted[pid] = patterns_accepted.get(pid, 0) + 1
        elif not changed and patterns:
            for pid in patterns:
                patterns_overridden[pid] = patterns_overridden.get(pid, 0) + 1
        elif changed and line_no not in flagged_line_nums:
            # user changed a line that wasn't flagged — potential new pattern
            orig_stripped = orig_lines[i].strip()
            if len(orig_stripped) > 40 and orig_stripped not in ("", "\n"):
                changed_unflagged[line_no] = orig_stripped[:240]

    total_changed = sum(1 for i in range(min_lines) if lines_changed_pct(orig_lines[i], acc_lines[i]))
    full_rewrite = total_changed > max(1, min_lines * 0.8)

    # session stats from accepted
    acc_sentences = sentences(accepted_text)
    acc_paragraphs = paragraphs(accepted_text)
    acc_sentence_lengths = [len(words(s)) for s in acc_sentences if words(s)]
    acc_paragraph_sentence_counts = [max(1, len(sentences(p))) for p in acc_paragraphs]
    avg_s = round(sum(acc_sentence_lengths) / len(acc_sentence_lengths), 1) if acc_sentence_lengths else 0
    avg_p = round(sum(acc_paragraph_sentence_counts) / len(acc_paragraph_sentence_counts), 1) if acc_paragraph_sentence_counts else 0

    # simplified new_removals: surface a sample of changed-unflagged lines for review
    new_removals = []
    seen_phrases: set[str] = set()
    for line_no in sorted(changed_unflagged):
        phrase = changed_unflagged[line_no]
        key = phrase.lower().strip()[:60]
        if key not in seen_phrases:
            seen_phrases.add(key)
            new_removals.append({"line": line_no, "original_text": phrase, "context": ""})
            if len(new_removals) >= 10:
                break

    report: dict[str, Any] = {
        "signal_version": SIGNAL_VERSION,
        "session": {
            "original_path": original_path,
            "accepted_path": accepted_path,
            "full_rewrite": full_rewrite,
        },
        "patterns_accepted": dict(sorted(patterns_accepted.items())),
        "patterns_overridden": dict(sorted(patterns_overridden.items())),
        "new_removals": new_removals,
        "session_stats": {
            "original_words": len(words(original_text)),
            "accepted_words": len(words(accepted_text)),
            "accepted_avg_sentence": avg_s,
            "accepted_avg_paragraph": avg_p,
            "accepted_sentence_count": len(acc_sentence_lengths),
            "accepted_paragraph_count": len(acc_paragraph_sentence_counts),
        },
    }
    return report


def _current_date() -> str:
    return datetime.date.today().isoformat()


def init_temporal_pattern(rule_id: str) -> dict[str, Any]:
    """create a new temporal pattern entry."""
    now = _current_date()
    return {
        "id": rule_id,
        "confidence": 0.0,
        "first_seen": now,
        "last_confirmed": now,
        "source_samples": [],  # list of sample paths that triggered this
        "contradictions": [],  # dates when pattern was flagged but overridden by user
        "superseded_by": None,
        "status": "active",
    }


def evolve_meta_from_signal(
    meta: dict[str, Any],
    patterns_accepted: dict[str, int],
    patterns_overridden: dict[str, int],
    source_samples: list[str] | None = None,
) -> dict[str, Any]:
    """update temporal pattern weights in meta based on accept/override signals.

    each pattern tracks: first_seen, last_confirmed, contradictions per date,
    source_samples, confidence (0.0-1.0), and status.
    """
    now = _current_date()
    temporal = meta.get("temporal_patterns", {})

    for rule_id, count in patterns_accepted.items():
        tp = temporal.get(rule_id)
        if tp is None:
            tp = init_temporal_pattern(rule_id)
            temporal[rule_id] = tp
        tp["last_confirmed"] = now
        if source_samples:
            for s in source_samples:
                if s not in tp["source_samples"]:
                    tp["source_samples"].append(s)
        # accepted signals boost confidence
        boost = min(count * 0.08, 0.40)  # cap boost per session
        tp["confidence"] = min(1.0, tp["confidence"] + boost)
        tp["status"] = "active"

    for rule_id, count in patterns_overridden.items():
        tp = temporal.get(rule_id)
        if tp is None:
            tp = init_temporal_pattern(rule_id)
            temporal[rule_id] = tp
        tp["contradictions"].append({"date": now, "count": count})
        # overridden signals decrease confidence faster
        penalty = min(count * 0.12, 0.50)
        tp["confidence"] = max(0.0, tp["confidence"] - penalty)
        # determine status
        if len(tp["contradictions"]) >= 3 and tp["confidence"] < 0.30:
            tp["status"] = "declining"
        if len(tp["contradictions"]) >= 5 and tp["confidence"] < 0.15:
            tp["status"] = "stale"

    # decay untouched patterns whose last_confirmed is > 14 days ago
    two_weeks_ms = 14 * 24 * 60 * 60
    for tp in temporal.values():
        last = tp.get("last_confirmed", now)
        try:
            last_date = datetime.date.fromisoformat(last)
            days_since = (datetime.date.today() - last_date).days
        except (ValueError, TypeError):
            days_since = 0
        if days_since > 14:
            decay = min(days_since * 0.005, 0.15)  # slow decay over time
            tp["confidence"] = max(0.0, tp["confidence"] - decay)
            if tp["confidence"] < PATTERN_CONFIDENCE_THRESHOLD and tp["status"] == "active":
                tp["status"] = "stale"

    meta["temporal_patterns"] = temporal
    meta["signal_version"] = META_SIGNAL_VERSION
    meta["last_updated"] = now
    meta["signal_count"] = meta.get("signal_count", 0) + sum(patterns_accepted.values()) + sum(patterns_overridden.values())

    return meta


def get_active_patterns(meta: dict[str, Any]) -> list[str]:
    """return rule_ids of patterns that are active and above confidence threshold."""
    temporal = meta.get("temporal_patterns", {})
    return [
        rid for rid, tp in temporal.items()
        if tp.get("status") == "active" and tp.get("confidence", 0) >= PATTERN_CONFIDENCE_THRESHOLD
    ]


def get_declining_patterns(meta: dict[str, Any]) -> list[str]:
    """return rule_ids that are declining or stale."""
    temporal = meta.get("temporal_patterns", {})
    return [rid for rid, tp in temporal.items() if tp.get("status") in ("declining", "stale")]


def filter_hits_by_weights(hits: list[dict[str, Any]], meta: dict[str, Any]) -> list[dict[str, Any]]:
    """remove hits for patterns that have been learned as not applicable to this voice."""
    temporal = meta.get("temporal_patterns", {})
    if not temporal:
        return hits
    declined = {}
    for rid, tp in temporal.items():
        if tp.get("status") in ("declining", "stale"):
            declined[rid] = tp.get("confidence", 0)
    if not declined:
        return hits
    return [h for h in hits if h.get("rule") not in declined]


def evolve_profile(
    profile: dict[str, Any],
    meta: dict[str, Any],
    original_text: str,
    accepted_text: str,
    original_path: str = "original",
    accepted_path: str = "accepted",
    new_samples_text: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """one-shot evolution: extract signals + update meta + merge profile stats.

    this is the core auto-improvement function. after every writing session:
    1. diff original vs accepted to extract accept/override signals
    2. update temporal pattern weights in meta
    3. merge new sample stats into the profile if new_samples_text is provided
    4. filter out declining/stale patterns

    returns (updated_profile, updated_meta).
    """
    signal = build_signal_report(original_path, accepted_path, original_text, accepted_text, profile)
    meta = evolve_meta_from_signal(
        meta, signal["patterns_accepted"], signal["patterns_overridden"],
        source_samples=[original_path],
    )
    if new_samples_text:
        profile = update_profile(profile, new_samples_text.strip())
    return profile, meta


def update_profile(profile: dict[str, Any], new_samples_text: str) -> dict[str, Any]:
    """merge new writing samples into an existing profile using rolling averages.

    the existing profile's stats are weighted by source_count. new stats
    get their own count. values that aren't simple averages (opening_moves,
    anchors) use a merge strategy rather than a formula.
    """
    sentence_list = sentences(new_samples_text)
    paragraph_list = paragraphs(new_samples_text)
    sentence_lengths = [len(words(s)) for s in sentence_list if words(s)]
    paragraph_sentence_counts = [max(1, len(sentences(p))) for p in paragraph_list]

    old_count = profile.get("source_count", 1)
    new_count = 1  # treating this update as one new source
    total_count = old_count + new_count

    # rolling average for sentence length
    old_avg_words = profile.get("sentence", {}).get("avg_words", 0)
    new_avg_words = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0
    if old_avg_words and new_avg_words:
        merged_avg_words = round((old_avg_words * old_count + new_avg_words * new_count) / total_count, 1)
    else:
        merged_avg_words = old_avg_words or new_avg_words

    # rolling average for paragraph length
    old_avg_par = profile.get("paragraph", {}).get("avg_sentences", 0)
    new_avg_par = round(sum(paragraph_sentence_counts) / len(paragraph_sentence_counts), 1) if paragraph_sentence_counts else 0
    if old_avg_par and new_avg_par:
        merged_avg_par = round((old_avg_par * old_count + new_avg_par * new_count) / total_count, 1)
    else:
        merged_avg_par = old_avg_par or new_avg_par

    # merge opening moves: keep old ones, prepend new top moves
    existing_moves = profile.get("signature", {}).get("opening_moves", [])
    new_moves = top_opening_moves(paragraph_list, 4)
    merged_moves = list(dict.fromkeys(new_moves + existing_moves))[:8]

    # merge anchors: keep old anchors, insert new ones that aren't near-duplicates
    existing_anchors = profile.get("signature", {}).get("anchors", [])
    new_anchors = choose_anchors(paragraph_list, 2)
    seen = {a[:80].lower() for a in existing_anchors}
    for anchor in new_anchors:
        if anchor[:80].lower() not in seen:
            seen.add(anchor[:80].lower())
            existing_anchors.append(anchor)
            if len(existing_anchors) >= 5:
                break

    # rebuild variance label using combined length estimate
    # we approximate the combined variance since we don't store raw lengths
    # conservative: keep old variance unless new samples strongly suggest otherwise
    new_variance = variance_label(sentence_lengths) if len(sentence_lengths) >= 3 else None
    old_variance = profile.get("sentence", {}).get("variance", "medium")
    merged_variance = new_variance if new_variance and new_variance != old_variance else old_variance

    # update cadence
    existing_cadence = profile.get("signature", {}).get("cadence", [])
    updated_cadence = [
        f"average sentence length around {merged_avg_words} words",
        f"sentence length variance is {merged_variance}",
        f"average paragraph length around {merged_avg_par} sentences",
    ]
    case_style = profile.get("signature", {}).get("case_style", "mixed")
    if case_style == "mostly lowercase" and "leans lowercase in visible prose" not in [c for c in updated_cadence]:
        updated_cadence.append("leans lowercase in visible prose")

    # rebuild profile
    profile["source_count"] = total_count
    profile["word_count"] = profile.get("word_count", 0) + len(words(new_samples_text))
    profile["sentence"] = {"avg_words": merged_avg_words, "variance": merged_variance}
    profile["paragraph"] = {"avg_sentences": merged_avg_par}
    profile["signature"]["opening_moves"] = merged_moves
    profile["signature"]["anchors"] = existing_anchors[:5]
    profile["signature"]["cadence"] = updated_cadence

    return profile


def cmd_profile_update(args: argparse.Namespace) -> int:
    """merge new samples into an existing profile."""
    profile_path = Path(args.profile).expanduser()
    if not profile_path.exists():
        raise SystemExit(f"profile not found: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8", errors="ignore"))

    combined_text = ""
    for raw_path in args.paths:
        files = iter_text_files([raw_path])
        for path in files:
            combined_text += "\n\n" + read_text(path)

    if not combined_text.strip():
        print("no new text samples found; profile unchanged")
        return 0

    profile = update_profile(profile, combined_text.strip())
    rendered = json.dumps(profile, indent=2, ensure_ascii=False)
    write_or_print(rendered, args.out)
    return 0


def cmd_profile_export(args: argparse.Namespace) -> int:
    """bundle a profile + optional meta into a portable .hyv file."""
    profile_path = Path(args.profile).expanduser()
    if not profile_path.exists():
        raise SystemExit(f"profile not found: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8", errors="ignore"))

    bundle: dict[str, Any] = {
        "bundle_version": "hold-your-voice-bundle-v1",
        "exported_at": datetime.datetime.now().isoformat()[:19],
        "profile": profile,
    }
    if args.meta:
        meta_path = Path(args.meta).expanduser()
        if meta_path.exists():
            bundle["meta"] = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
    write_or_print(json.dumps(bundle, indent=2, ensure_ascii=False), args.out)
    return 0


def cmd_profile_import(args: argparse.Namespace) -> int:
    """import a .hyv bundle into a destination profile."""
    source_path = Path(args.source).expanduser()
    if not source_path.exists():
        raise SystemExit(f"source not found: {source_path}")
    source = json.loads(source_path.read_text(encoding="utf-8", errors="ignore"))
    if source.get("bundle_version") != "hold-your-voice-bundle-v1":
        raise SystemExit(f"unknown bundle version: {source.get('bundle_version')}")

    dest_profile: dict[str, Any]
    dest_path = Path(args.profile).expanduser()
    if dest_path.exists():
        dest_profile = json.loads(dest_path.read_text(encoding="utf-8", errors="ignore"))
    else:
        dest_profile = {}

    source_profile = source.get("profile", {})
    src_count = source_profile.get("source_count", 0)
    dest_count = dest_profile.get("source_count", 0)

    # if destination is empty, this is a pure copy of the source profile
    if not dest_profile:
        dest_profile = dict(source_profile)
        write_or_print(json.dumps(dest_profile, indent=2, ensure_ascii=False), args.profile)
        print(f"imported into {args.profile}")
        # merge meta still applies
        _merge_import_meta(source, args, args.profile)
        return 0

    src_count = source_profile.get("source_count", 0)
    dest_count = dest_profile.get("source_count", 0)

    # merge profile: prefer higher source_count for stats
    if src_count > dest_count:
        # source has more signal; take its stats
        dest_profile["source_count"] = dest_count + src_count
        dest_profile["word_count"] = dest_profile.get("word_count", 0) + source_profile.get("word_count", 0)
        dest_profile["sentence"] = source_profile.get("sentence", {})
        dest_profile["paragraph"] = source_profile.get("paragraph", {})
        # merge signature fields
        dest_sig = dest_profile.get("signature", {})
        src_sig = source_profile.get("signature", {})
        merged_moves = list(dict.fromkeys(src_sig.get("opening_moves", []) + dest_sig.get("opening_moves", [])))[:8]
        merged_anchors = list(dict.fromkeys(src_sig.get("anchors", []) + dest_sig.get("anchors", [])))[:5]
        merged_never = list(dict.fromkeys(src_sig.get("never_list", DEFAULT_NEVER_LIST) + dest_sig.get("never_list", DEFAULT_NEVER_LIST)))
        dest_sig["opening_moves"] = merged_moves
        dest_sig["anchors"] = merged_anchors
        dest_sig["never_list"] = merged_never
        dest_profile["signature"] = dest_sig
    else:
        # destination has more or equal signal; keep its stats, merge in source anchors/moves
        dest_profile["source_count"] = dest_count + src_count
        dest_profile["word_count"] = dest_profile.get("word_count", 0) + source_profile.get("word_count", 0)
        dest_sig = dest_profile.get("signature", {})
        src_sig = source_profile.get("signature", {})
        merged_moves = list(dict.fromkeys(dest_sig.get("opening_moves", []) + src_sig.get("opening_moves", [])))[:8]
        merged_anchors = list(dict.fromkeys(dest_sig.get("anchors", []) + src_sig.get("anchors", [])))[:5]
        dest_sig["opening_moves"] = merged_moves
        dest_sig["anchors"] = merged_anchors
        dest_profile["signature"] = dest_sig

    # merge meta if present
    write_or_print(json.dumps(dest_profile, indent=2, ensure_ascii=False), args.profile)
    print(f"imported into {args.profile}", end="")
    _merge_import_meta(source, args, str(dest_path))
    print()
    return 0


def _merge_import_meta(source: dict[str, Any], args: argparse.Namespace, dest_profile_path: str) -> None:
    """merge meta from a .hyv bundle into a destination meta file."""
    source_meta = source.get("meta", {})
    if not source_meta:
        return

    meta_path_str = args.meta
    if meta_path_str:
        mpath = Path(meta_path_str).expanduser()
    else:
        mpath = Path(dest_profile_path).with_suffix(".meta.json")

    dest_meta: dict[str, Any] = {}
    if mpath.exists():
        try:
            dest_meta = json.loads(mpath.read_text(encoding="utf-8", errors="ignore"))
        except (json.JSONDecodeError, OSError):
            dest_meta = {}

    # merge pattern_weights: take higher signal_count
    dest_weights = dest_meta.get("pattern_weights", {})
    src_weights = source_meta.get("pattern_weights", {})
    for key, src_w in src_weights.items():
        if key not in dest_weights or src_w > dest_weights[key]:
            dest_weights[key] = src_w
    if src_weights:
        dest_meta["pattern_weights"] = dest_weights
    dest_meta["signal_count"] = dest_meta.get("signal_count", 0) + source_meta.get("signal_count", 0)

    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(dest_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f" + {mpath}")


def render_voice_md(profile: dict[str, Any], meta: dict[str, Any]) -> str:
    """render voice.md — the human-readable voice profile summary."""
    lines: list[str] = []
    name = profile.get("name", "unnamed")
    lines.append(f"# voice for {name}")
    lines.append("")
    lines.append("> continuously learned by hold your voice from your writing signals")
    lines.append("")

    # temporal pattern weights
    temporal = meta.get("temporal_patterns", {})
    signal_count = meta.get("signal_count", 0)
    if temporal:
        lines.append("# evolved pattern weights")
        lines.append("")
        lines.append("| pattern | confidence | status | confirmed |")
        lines.append("|---------|-----------|--------|-----------|")
        sorted_patterns = sorted(temporal.items(), key=lambda x: -x[1].get("confidence", 0))
        for pid, tp in sorted_patterns:
            w = tp.get("confidence", 0)
            s = tp.get("status", "active")
            c = tp.get("last_confirmed", "?")
            lines.append(f"| {pid} | {w:.2f} | {s} | {c} |")
        if signal_count:
            lines.append("")
            lines.append(f"_(based on {signal_count} signals)_")
        lines.append("")

    # voice stats section
    lines.append("# voice stats")
    lines.append("")
    sentence = profile.get("sentence", {})
    paragraph = profile.get("paragraph", {})
    lines.append(f"- sentence length: {sentence.get('avg_words', '?')} words avg (`{sentence.get('variance', '?')}` variance)")
    lines.append(f"- paragraph length: {paragraph.get('avg_sentences', '?')} sentences avg")
    sig = profile.get("signature", {})
    lines.append(f"- case style: {sig.get('case_style', '?')}")
    lines.append(f"- argument pattern: {sig.get('argument_pattern', '?')}")
    lines.append("")

    # cadence
    cadence = sig.get("cadence", [])
    if cadence:
        lines.append("# cadence")
        lines.append("")
        for note in cadence:
            lines.append(f"- {note}")
        lines.append("")

    # opening moves
    moves = sig.get("opening_moves", [])
    if moves:
        lines.append("# opening moves")
        lines.append("")
        for i, move in enumerate(moves[:6], 1):
            lines.append(f"{i}. \"{move}...\"")
        lines.append("")

    # never list
    never_list = sig.get("never_list", [])
    if never_list:
        lines.append("# banned patterns")
        lines.append("")
        for phrase in never_list:
            lines.append(f"- {phrase}")
        lines.append("")

    # anchors
    anchors = sig.get("anchors", [])
    if anchors:
        lines.append("# voice anchors")
        lines.append("")
        for anchor in anchors[:3]:
            lines.append(f"> {anchor[:240]}")
            lines.append("")

    # sources
    sources = profile.get("sources", [])
    if sources:
        lines.append("# sources")
        lines.append(f"profile built from {profile.get('source_count', len(sources))} source(s):")
        for s in sources[:10]:
            lines.append(f"- [{s.get('path', '?')}]({s.get('path', '?')}) ({s.get('chars', 0)} chars)")
        lines.append("")

    # meta
    if signal_count:
        lines.append("*last updated: {0} | signals processed: {1}*".format(meta.get("last_updated", "unknown"), signal_count))
        lines.append("")

    return "\n".join(lines)


def cmd_profile_status(args: argparse.Namespace) -> int:
    """pretty-print the learning state of a profile."""
    profile_path = Path(args.profile).expanduser()
    if not profile_path.exists():
        raise SystemExit(f"profile not found: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8", errors="ignore"))

    # try to load meta if present
    meta: dict[str, Any] = {}
    meta_path = None
    meta_path_str = args.meta
    if meta_path_str:
        meta_path = Path(meta_path_str).expanduser()
    else:
        meta_path = profile_path.with_suffix(".meta.json")
    if meta_path and meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
        except (json.JSONDecodeError, OSError):
            meta = {}

    lines: list[str] = []

    # header
    name = profile.get("name", "unnamed")
    ver = profile.get("profile_version", "?")
    lines.append(f"voice profile: {name}")
    lines.append(f"  version: {ver}")
    lines.append(f"  source_count: {profile.get('source_count', 0)}")
    lines.append(f"  word_count: {profile.get('word_count', 0)}")
    signal_count = meta.get("signal_count", 0)
    lines.append(f"  signals_processed: {signal_count}")
    if meta.get("last_updated"):
        lines.append(f"  last_updated: {meta['last_updated']}")
    lines.append("")

    # temporal pattern weights
    temporal = meta.get("temporal_patterns", {})
    if temporal:
        lines.append("pattern weights (evolved):")
        lines.append(f"  {'pattern':<35} {'confidence':<12} {'status':<12} {'confirmed':<12}")
        lines.append(f"  {'─'*34:<35} {'─'*11:<12} {'─'*11:<12} {'─'*11:<12}")
        sorted_patterns = sorted(temporal.items(), key=lambda x: -x[1].get("confidence", 0))
        for pid, tp in sorted_patterns:
            w = tp.get("confidence", 0)
            bar_len = int(w * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            status = tp.get("status", "active")
            confirmed = tp.get("last_confirmed", "?")
            lines.append(f"  {pid:<35} {bar} {w:.2f}     {status:<12} {confirmed:<12}")
        lines.append("")

    # voice stats
    lines.append("voice stats:")
    sentence = profile.get("sentence", {})
    paragraph = profile.get("paragraph", {})
    lines.append(f"  sentence length:   {sentence.get('avg_words', '?')} words avg ({sentence.get('variance', '?')} variance)")
    lines.append(f"  paragraph length:  {paragraph.get('avg_sentences', '?')} sentences avg")
    sig = profile.get("signature", {})
    lines.append(f"  case style:        {sig.get('case_style', '?')}")
    lines.append(f"  argument pattern:  {sig.get('argument_pattern', '?')}")
    lines.append("")

    # opening moves
    moves = sig.get("opening_moves", [])
    if moves:
        lines.append("top opening moves:")
        for i, move in enumerate(moves[:6], 1):
            lines.append(f"  {i}. \"{move}...\"")
        lines.append("")

    # never_list
    never_list = sig.get("never_list", [])
    if never_list:
        lines.append(f"banned phrases: {len(never_list)}")
        for phrase in never_list[:8]:
            lines.append(f"  - {phrase}")
        lines.append("")

    # sources
    sources = profile.get("sources", [])
    if sources:
        lines.append(f"sources ({len(sources)}):")
        for s in sources[:5]:
            lines.append(f"  - {s.get('path', '?')} ({s.get('chars', 0)} chars)")
        if len(sources) > 5:
            lines.append(f"  ... and {len(sources) - 5} more")
        lines.append("")

    print("\n".join(lines))

    # optionally write taste markdown
    if args.write_voice:
        voice_md = render_voice_md(profile, meta)
        voice_path = args.write_voice
        if voice_path == "-":
            print("--- voice.md ---")
            print(voice_md)
        else:
            out_path = Path(voice_path).expanduser()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(voice_md, encoding="utf-8")
            print(f"\nvoice written to {out_path}")

    return 0


def cmd_reinforce(args: argparse.Namespace) -> int:
    """diff original vs accepted draft and emit a signal report."""
    orig_path, orig_text = load_draft(args.original)
    acc_path, acc_text = load_draft(args.accepted)
    profile: dict[str, Any] | None = None
    if args.profile:
        p = Path(args.profile).expanduser()
        if not p.exists():
            raise SystemExit(f"profile not found: {p}")
        profile = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    report = build_signal_report(orig_path, acc_path, orig_text, acc_text, profile)
    write_or_print(json.dumps(report, indent=2, ensure_ascii=False), args.out)
    return 0


def cmd_profile_evolve(args: argparse.Namespace) -> int:
    """one-shot evolution: extract signals, update meta, merge profile stats."""
    profile_path = Path(args.profile).expanduser()
    if not profile_path.exists():
        raise SystemExit(f"profile not found: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8", errors="ignore"))

    meta_path = Path(args.meta).expanduser() if args.meta else profile_path.with_suffix(".meta.json")
    meta: dict[str, Any] = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
        except (json.JSONDecodeError, OSError):
            meta = {}

    orig_path, orig_text = load_draft(args.original)
    acc_path, acc_text = load_draft(args.accepted)

    new_samples_text: str | None = None
    if args.new_samples:
        parts = []
        for raw_path in args.new_samples:
            files = iter_text_files([raw_path])
            for f in files:
                parts.append(read_text(f))
        if parts:
            new_samples_text = "\n\n".join(parts)

    profile, meta = evolve_profile(
        profile, meta, orig_text, acc_text,
        original_path=orig_path, accepted_path=acc_path,
        new_samples_text=new_samples_text,
    )

    profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    active = get_active_patterns(meta)
    declining = get_declining_patterns(meta)
    print(f"evolved {profile_path}")
    print(f"  meta: {meta_path}")
    print(f"  active patterns: {len(active)}")
    print(f"  declining/stale: {len(declining)}")
    print(f"  total signals: {meta.get('signal_count', 0)}")

    synced = _auto_sync(profile_path, meta_path)
    if synced:
        print(f"  synced to cloud (R2)")
    return 0


def write_or_print(value: str, out: str | None) -> None:
    if out:
        output_path = Path(out).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(value, encoding="utf-8")
        print(output_path)
    else:
        print(value)


def cmd_profile(args: argparse.Namespace) -> int:
    profile = build_profile(args.paths, args.name)
    rendered = json.dumps(profile, indent=2, ensure_ascii=False)
    write_or_print(rendered, args.out)
    return 0


def _auto_sync(profile_path: Path, meta_path: Path) -> bool:
    """try to sync to cloud if hold_voice_sync.py is available and env is configured.
    syncs only if > 23h since last sync. fails silently if sync script or boto3 is missing."""
    sync_script = Path(__file__).resolve().parent / "hold_voice_sync.py"
    if not sync_script.exists():
        return False
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(sync_script), "--profile", str(profile_path), "--meta", str(meta_path)],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def cmd_scan(args: argparse.Namespace) -> int:
    meta: dict[str, Any] = {}
    if args.meta:
        meta_path = Path(args.meta).expanduser()
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
            except (json.JSONDecodeError, OSError):
                pass

    results = []
    text_outputs = []
    had_hits = False
    for raw_path in args.paths:
        name, text = load_draft(raw_path)
        hits = scan_text(text)
        if meta:
            hits = filter_hits_by_weights(hits, meta)
        had_hits = had_hits or bool(hits)
        results.append({"path": name, "issue_count": len(hits), "issues": hits})
        text_outputs.append(format_scan_text(name, text, hits))

    if args.format == "json":
        print(json.dumps({"files": results}, indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(text_outputs))

    return 2 if args.fail_on_hit and had_hits else 0


def cmd_rewrite_prompt(args: argparse.Namespace) -> int:
    draft_name, draft = load_draft(args.draft)
    profile_text = None
    if args.profile:
        profile_path = Path(args.profile).expanduser()
        if not profile_path.exists():
            raise SystemExit(f"profile not found: {profile_path}")
        profile_text = profile_path.read_text(encoding="utf-8", errors="ignore")
    meta: dict[str, Any] | None = None
    if args.meta:
        meta_path = Path(args.meta).expanduser()
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
            except (json.JSONDecodeError, OSError):
                meta = None
    prompt = build_rewrite_prompt(draft_name, draft, profile_text, args.constraints or "", meta=meta)
    write_or_print(prompt, args.out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable Hold Your Voice helpers")
    sub = parser.add_subparsers(dest="command", required=True)

    profile = sub.add_parser("profile", help="build a voice profile from sample files or directories")
    profile.add_argument("paths", nargs="+", help="sample files or directories")
    profile.add_argument("--name", default="project voice", help="profile name")
    profile.add_argument("--out", help="write profile JSON to this path")
    profile.set_defaults(func=cmd_profile)

    scan = sub.add_parser("scan", help="scan drafts for AI-writing patterns")
    scan.add_argument("paths", nargs="+", help="draft files, or '-' for stdin")
    scan.add_argument("--format", choices=["json", "text"], default="json")
    scan.add_argument("--fail-on-hit", action="store_true", help="exit 2 when issues are found")
    scan.add_argument("--meta", help="meta JSON file for learned pattern filtering")
    scan.set_defaults(func=cmd_scan)

    rewrite = sub.add_parser("rewrite-prompt", help="generate a line-level rewrite prompt")
    rewrite.add_argument("draft", help="draft file, or '-' for stdin")
    rewrite.add_argument("--profile", help="voice profile JSON file")
    rewrite.add_argument("--constraints", default="", help="extra rewrite constraints")
    rewrite.add_argument("--out", help="write prompt to this path")
    rewrite.add_argument("--meta", help="meta JSON file for learned pattern filtering")
    rewrite.set_defaults(func=cmd_rewrite_prompt)

    pu = sub.add_parser("profile-update", help="merge new writing samples into an existing profile using rolling averages")
    pu.add_argument("--profile", required=True, help="existing profile JSON file")
    pu.add_argument("paths", nargs="+", help="new sample files or directories")
    pu.add_argument("--out", help="write updated profile to this path (default: in-place)")
    pu.set_defaults(func=cmd_profile_update)

    pex = sub.add_parser("profile-export", help="bundle a voice profile into a portable .hyv file")
    pex.add_argument("--profile", required=True, help="voice profile JSON file")
    pex.add_argument("--meta", help="optional signal meta JSON file to include")
    pex.add_argument("--out", required=True, help="output .hyv file path")
    pex.set_defaults(func=cmd_profile_export)

    pim = sub.add_parser("profile-import", help="import a .hyv bundle into a destination profile")
    pim.add_argument("--profile", required=True, help="destination profile JSON file (will be updated)")
    pim.add_argument("--meta", help="destination meta JSON file path (default: profile path with .meta.json)")
    pim.add_argument("--source", required=True, help=".hyv bundle file to import from")
    pim.set_defaults(func=cmd_profile_import)

    pst = sub.add_parser("profile-status", help="pretty-print the learning state of a profile")
    pst.add_argument("--profile", required=True, help="voice profile JSON file")
    pst.add_argument("--meta", help="signal meta JSON file (default: profile path with .meta.json)")
    pst.add_argument("--write-voice", nargs="?", const="-", default=None,
                     help="write voice.md (optional path; no arg = stdout)")
    pst.set_defaults(func=cmd_profile_status)

    reinforce = sub.add_parser("reinforce", help="diff original vs accepted draft to extract learning signals")
    reinforce.add_argument("--original", required=True, help="original draft file, or '-' for stdin")
    reinforce.add_argument("--accepted", required=True, help="accepted/final draft file, or '-' for stdin")
    reinforce.add_argument("--profile", help="voice profile JSON file (optional)")
    reinforce.add_argument("--out", help="write signal report to this path")
    reinforce.set_defaults(func=cmd_reinforce)

    pev = sub.add_parser("profile-evolve", help="one-shot evolution: signal extraction + meta update + profile merge")
    pev.add_argument("--original", required=True, help="original (AI) draft file, or '-' for stdin")
    pev.add_argument("--accepted", required=True, help="accepted (user-edited) draft file, or '-' for stdin")
    pev.add_argument("--profile", required=True, help="voice profile JSON file")
    pev.add_argument("--meta", help="meta JSON file path (default: profile path with .meta.json)")
    pev.add_argument("--new-samples", nargs="*", default=None, help="additional new writing samples to merge (optional)")
    pev.set_defaults(func=cmd_profile_evolve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

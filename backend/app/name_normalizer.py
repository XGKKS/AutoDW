import re
from typing import Iterable, List, Optional


PROTECTED_ACRONYMS = {"PDC", "SKU", "SPU", "ID", "API"}
PROTECTED_ACRONYMS_LOWER = {item.lower() for item in PROTECTED_ACRONYMS}
VALIDATION_ROOT_TOKENS = {
    "main",
    "damaged",
    "part",
    "maximum",
    "minimum",
    "average",
    "speed",
    "pdc",
    "follow",
    "up",
    "visit",
}

# Canonical concept roots keep the same English root across synonymous Chinese phrases.
CANONICAL_CONCEPT_ROOTS = {
    "主损件": "main_damaged_part",
    "主店": "main_store",
}

# Exact field-level overrides for noisy phrases.
FIELD_IDENTIFIER_OVERRIDES = [
    (re.compile(r"^(?:PDC|pdc)(?:\s*跟进)?状态$"), "pdc_status"),
    (re.compile(r"^最大车速$"), "maximum_speed"),
]

# Optional helpers for common noise tokens.
NOISE_TOKENS = {"跟进"}

BRACKET_CONTENT_PATTERN = re.compile(
    r"[\(\（\[\【\<《][^()\[\]（）【】<>《》]*[\)\）\]\】\>》]"
)
WHITESPACE_PATTERN = re.compile(r"\s+")
UNDERSCORE_PATTERN = re.compile(r"_+")


class NameNormalizer:
    def __init__(self) -> None:
        self.protected_acronyms = set(PROTECTED_ACRONYMS)
        self.canonical_concept_roots = dict(CANONICAL_CONCEPT_ROOTS)

    def iter_custom_terms(self) -> List[str]:
        terms = set(self.protected_acronyms)
        terms.update(self.canonical_concept_roots.keys())
        for pattern, _ in FIELD_IDENTIFIER_OVERRIDES:
            # Keep the most useful literal terms in the jieba user dictionary.
            literal = pattern.pattern.replace("^(?:PDC|pdc)(?:\\s*跟进)?状态$", "PDC状态")
            literal = literal.replace("^最大车速$", "最大车速")
            terms.add(literal)
        return sorted(terms)

    def clean_chinese_text(self, text: str) -> str:
        if not text:
            return ""

        cleaned = str(text).strip()
        previous = None
        while cleaned and cleaned != previous:
            previous = cleaned
            cleaned = BRACKET_CONTENT_PATTERN.sub("", cleaned)

        cleaned = cleaned.replace("　", " ")
        cleaned = WHITESPACE_PATTERN.sub(" ", cleaned)
        cleaned = cleaned.replace(" ", "")
        return cleaned.strip("`\"'，,。；;：:()（）[]【】<>《》_-")

    def normalize_english_identifier(self, identifier: str) -> str:
        if not identifier:
            return ""

        normalized = str(identifier).strip().strip("`\"'")
        normalized = normalized.replace("-", "_").replace(".", "_").replace("/", "_")
        normalized = WHITESPACE_PATTERN.sub("_", normalized)
        normalized = UNDERSCORE_PATTERN.sub("_", normalized)
        return normalized.strip("_").lower()

    def get_field_override(self, chinese_name: str) -> Optional[str]:
        cleaned = self.clean_chinese_text(chinese_name)
        if not cleaned:
            return None

        for pattern, english_name in FIELD_IDENTIFIER_OVERRIDES:
            if pattern.fullmatch(cleaned):
                return english_name

        return None

    def canonical_root_for_token(self, token: str) -> Optional[str]:
        if not token:
            return None

        token = str(token).strip()
        if not token:
            return None

        if token in self.canonical_concept_roots:
            return self.canonical_concept_roots[token]

        upper = token.upper()
        if upper in self.protected_acronyms:
            return upper.lower()

        if token.lower() in PROTECTED_ACRONYMS_LOWER:
            return token.lower()

        return None

    def tokenize_chinese_name(self, chinese_name: str, tokenizer) -> List[str]:
        cleaned = self.clean_chinese_text(chinese_name)
        if not cleaned:
            return []

        tokens = tokenizer(cleaned, cut_all=False) if tokenizer else [cleaned]
        tokens = [token.strip() for token in tokens if token and token.strip()]

        has_protected_acronym = any(token.upper() in self.protected_acronyms for token in tokens)
        normalized_tokens: List[str] = []
        for token in tokens:
            if has_protected_acronym and token in NOISE_TOKENS:
                continue

            canonical = self.canonical_root_for_token(token)
            if canonical:
                normalized_tokens.append(canonical)
            else:
                normalized_tokens.append(token)

        return normalized_tokens

    def normalize_identifier_tokens(self, identifier: str) -> List[str]:
        normalized = self.normalize_english_identifier(identifier)
        return [part for part in normalized.split("_") if part]

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

_analyzer = None
_anonymizer = None


def _get_analyzer() -> AnalyzerEngine:
    global _analyzer
    if _analyzer is None:
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        })
        _analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])
    return _analyzer


def _get_anonymizer() -> AnonymizerEngine:
    global _anonymizer
    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()
    return _anonymizer


def remove_pii(text: str) -> str:
    if not text:
        return text
    results = _get_analyzer().analyze(text=text, language="en")
    anonymized = _get_anonymizer().anonymize(text=text, analyzer_results=results)
    return anonymized.text

def has_pii(text: str) -> bool:
    if not text:
        return False
    results = _get_analyzer().analyze(text=text, language="en")
    return len(results) > 0
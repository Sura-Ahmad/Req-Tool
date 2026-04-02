from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def remove_pii(text: str) -> str:
    if not text:
        return text
    results = analyzer.analyze(text=text, language="en")
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text

def has_pii(text: str) -> bool:
    if not text:
        return False
    results = analyzer.analyze(text=text, language="en")
    return len(results) > 0
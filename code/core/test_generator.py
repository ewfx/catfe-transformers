# core/test_generator.py
import openai
import json
import uuid
import hashlib
from datetime import datetime
from config import settings

class TestGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_test_case(self, use_case: dict) -> dict:
        prompt = f"""As a senior financial QA architect, generate comprehensive test cases for banking systems. Follow this structure:

[REQUIRED FORMAT]
### Financial Domain: {use_case.get('category', 'Compliance')}
### Use Case: {use_case['use_case']}
### Risk Level: {use_case.get('risk', 'High')}

**Positive Scenario**:
1. [Valid transaction details]
2. [System should process correctly]
3. [Expected successful outcome]

**Negative Scenarios**:
- [Fraudulent transaction pattern]
- [Regulatory violation attempt]
- [Edge case exploitation]

**Validation Criteria**:
- [Compliance check] (e.g., OFAC, AML)
- [Fraud detection logic] 
- [System performance metrics] (response time < 500ms)

**Test Data Requirements**:
- [Specific transaction amounts]
- [Currency combinations]
- [High-risk jurisdiction examples]

**Edge Cases**:
- [Time zone differences in transaction timing]
- [Partial name matches in sanctions lists]
- [Currency conversion rounding issues]

[EXAMPLES]
For Sanctions Checking:
- Positive: $9,999 transfer to non-sanctioned entity
- Negative: $10,001 transfer split across 2 transactions to sanctioned country
"""

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "system",
                "content": """You are a financial systems testing expert with 15 years experience in banking. 
                Consider: SWIFT message formats, ISO 20022 standards, Basel III requirements, and real-world fraud patterns."""
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.4,
            max_tokens=2000
        )
        
        return self._parse_response(response.choices[0].message.content, use_case)

    def _parse_response(self, response: str, use_case: dict) -> dict:
        sections = {
            "positive_scenario": [],
            "negative_scenarios": [],
            "validation_criteria": [],
            "test_data": [],
            "edge_cases": [],
            "compliance_references": []
        }

        current_section = None
        section_map = {
            "positive scenario": "positive_scenario",
            "negative scenarios": "negative_scenarios",
            "validation criteria": "validation_criteria",
            "test data requirements": "test_data",
            "edge cases": "edge_cases",
            "compliance references": "compliance_references"
        }

        for line in response.split('\n'):
            line = line.strip()
            
            # Section detection
            lower_line = line.lower()
            for pattern, key in section_map.items():
                if pattern in lower_line:
                    current_section = key
                    break
            
            # Content parsing
            if current_section:
                if line.startswith(('1.', '2.', '- ', '*')):
                    clean_line = line.split('. ', 1)[-1].strip()
                    sections[current_section].append(clean_line)

        # Add financial domain fallbacks
        if not sections["negative_scenarios"]:
            sections["negative_scenarios"] = [
                f"Attempt {use_case['scenario']} with modified beneficiary details",
                "Test transaction just below reporting threshold ($9,999)",
                "Use mixed currency amounts to bypass detection"
            ]
            
        return {
            **use_case,
            **sections,
            "test_id": f"FINSEC-{uuid.uuid4().hex[:8]}",
            "hash": hashlib.sha256(response.encode()).hexdigest(),
            "last_updated": datetime.now().isoformat()
        }
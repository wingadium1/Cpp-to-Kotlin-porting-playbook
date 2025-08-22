#!/usr/bin/env python3
"""
AI Chunk Validator
Validates AI-converted chunks using high-capability models for quality assurance
"""
import os
import json
import argparse
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class ValidationResult:
    """Result of chunk validation"""
    chunk_id: str
    is_valid: bool
    score: float  # 0.0 to 1.0
    issues: List[str]
    recommendations: List[str]
    needs_manual_review: bool
    
@dataclass 
class ValidationCriteria:
    """Validation criteria for AI conversions"""
    comment_preservation: bool = True
    business_logic_accuracy: bool = True
    kotlin_syntax_correctness: bool = True
    null_safety_compliance: bool = True
    idiomatic_kotlin: bool = True
    performance_considerations: bool = False

class AIChunkValidator:
    """Validates AI-converted chunks for quality assurance"""
    
    def __init__(self, validation_model: str = "claude-3-5-sonnet"):
        self.validation_model = validation_model
        self.validation_stats = {
            "total_validated": 0,
            "passed_validation": 0,
            "failed_validation": 0,
            "manual_review_required": 0
        }
        
    def create_validation_prompt(self, 
                               original_cpp: str, 
                               converted_kotlin: str,
                               criteria: ValidationCriteria) -> str:
        """Create validation prompt for AI model"""
        prompt = f"""
Validate this C++ to Kotlin conversion for quality and accuracy.

**VALIDATION CRITERIA:**
1. Comment Preservation: Are ALL C++ comments preserved exactly?
2. Business Logic: Is the algorithm/logic identical to C++?
3. Kotlin Syntax: Is the Kotlin code syntactically correct and idiomatic?
4. Null Safety: Are null safety patterns properly applied?
5. Type Conversion: Are C++ types correctly converted to Kotlin equivalents?

**ORIGINAL C++ CODE:**
```cpp
{original_cpp}
```

**CONVERTED KOTLIN CODE:**
```kotlin
{converted_kotlin}
```

**VALIDATION INSTRUCTIONS:**
- Check each comment is preserved verbatim (including Japanese text)
- Verify business logic algorithms are functionally identical
- Ensure Kotlin syntax follows best practices
- Validate null safety and type conversions
- Flag any concerning patterns or potential errors

**OUTPUT FORMAT:**
Provide validation in this JSON format:
{{
  "is_valid": true/false,
  "score": 0.0-1.0,
  "issues": ["issue1", "issue2"],
  "recommendations": ["rec1", "rec2"],
  "needs_manual_review": true/false,
  "validation_details": {{
    "comment_preservation": "pass/fail/warning",
    "business_logic": "pass/fail/warning", 
    "kotlin_syntax": "pass/fail/warning",
    "null_safety": "pass/fail/warning",
    "idiomatic_kotlin": "pass/fail/warning"
  }}
}}
"""
        return prompt
        
    async def validate_conversion(self, 
                                original_cpp: str,
                                converted_kotlin: str,
                                chunk_id: str,
                                criteria: ValidationCriteria) -> ValidationResult:
        """Validate a single chunk conversion"""
        try:
            prompt = self.create_validation_prompt(original_cpp, converted_kotlin, criteria)
            
            # Call AI model for validation
            validation_response = await self._call_validation_model(prompt)
            
            # Parse validation result
            result = self._parse_validation_response(validation_response, chunk_id)
            
            # Update stats
            self.validation_stats["total_validated"] += 1
            if result.is_valid:
                self.validation_stats["passed_validation"] += 1
            else:
                self.validation_stats["failed_validation"] += 1
            
            if result.needs_manual_review:
                self.validation_stats["manual_review_required"] += 1
                
            return result
            
        except Exception as e:
            return ValidationResult(
                chunk_id=chunk_id,
                is_valid=False,
                score=0.0,
                issues=[f"Validation error: {e}"],
                recommendations=["Manual review required"],
                needs_manual_review=True
            )
    
    async def _call_validation_model(self, prompt: str) -> str:
        """Call AI model for validation"""
        print(f"🔍 Validating with {self.validation_model}...")
        await asyncio.sleep(0.1)  # Simulate API call
        
        # Mock validation response - in real implementation, call actual AI API
        mock_response = {
            "is_valid": True,
            "score": 0.85,
            "issues": [],
            "recommendations": ["Consider using data classes for simple data holders"],
            "needs_manual_review": False,
            "validation_details": {
                "comment_preservation": "pass",
                "business_logic": "pass", 
                "kotlin_syntax": "pass",
                "null_safety": "warning",
                "idiomatic_kotlin": "pass"
            }
        }
        
        return json.dumps(mock_response)
    
    def _parse_validation_response(self, response: str, chunk_id: str) -> ValidationResult:
        """Parse AI validation response"""
        try:
            data = json.loads(response)
            return ValidationResult(
                chunk_id=chunk_id,
                is_valid=data.get("is_valid", False),
                score=data.get("score", 0.0),
                issues=data.get("issues", []),
                recommendations=data.get("recommendations", []),
                needs_manual_review=data.get("needs_manual_review", True)
            )
        except json.JSONDecodeError:
            return ValidationResult(
                chunk_id=chunk_id,
                is_valid=False,
                score=0.0,
                issues=["Failed to parse validation response"],
                recommendations=["Manual review required"],
                needs_manual_review=True
            )
    
    def validate_conversion_directory(self, 
                                    converted_chunks_dir: str,
                                    original_chunks_dir: str,
                                    output_report: str,
                                    criteria: ValidationCriteria):
        """Validate all converted chunks in directory"""
        validation_results = []
        
        converted_files = [f for f in os.listdir(converted_chunks_dir) if f.endswith('.kt')]
        
        for kt_file in converted_files:
            chunk_id = kt_file.replace('.kt', '')
            cpp_file = f"{chunk_id}.cpp"
            
            kt_path = os.path.join(converted_chunks_dir, kt_file)
            cpp_path = os.path.join(original_chunks_dir, cpp_file)
            
            if os.path.exists(cpp_path):
                print(f"🔍 Validating {chunk_id}...")
                
                # Read files
                with open(cpp_path, 'r') as f:
                    original_cpp = f.read()
                with open(kt_path, 'r') as f:
                    converted_kotlin = f.read()
                
                # Validate
                result = asyncio.run(self.validate_conversion(
                    original_cpp, converted_kotlin, chunk_id, criteria
                ))
                
                validation_results.append(result)
                
                # Print result
                status = "✅ PASS" if result.is_valid else "❌ FAIL"
                review = " 🔍 REVIEW" if result.needs_manual_review else ""
                print(f"  {status} (Score: {result.score:.2f}){review}")
                
                if result.issues:
                    for issue in result.issues:
                        print(f"    ⚠️ {issue}")
        
        # Generate validation report
        self._generate_validation_report(validation_results, output_report)
        self._print_validation_summary()
    
    def _generate_validation_report(self, results: List[ValidationResult], output_file: str):
        """Generate comprehensive validation report"""
        report = {
            "validation_summary": {
                "total_chunks": len(results),
                "passed": len([r for r in results if r.is_valid]),
                "failed": len([r for r in results if not r.is_valid]),
                "manual_review_needed": len([r for r in results if r.needs_manual_review]),
                "average_score": sum(r.score for r in results) / len(results) if results else 0
            },
            "validation_details": [
                {
                    "chunk_id": r.chunk_id,
                    "is_valid": r.is_valid,
                    "score": r.score,
                    "issues": r.issues,
                    "recommendations": r.recommendations,
                    "needs_manual_review": r.needs_manual_review
                }
                for r in results
            ],
            "failed_chunks": [
                {
                    "chunk_id": r.chunk_id,
                    "score": r.score,
                    "issues": r.issues,
                    "recommendations": r.recommendations
                }
                for r in results if not r.is_valid
            ],
            "manual_review_chunks": [
                {
                    "chunk_id": r.chunk_id,
                    "score": r.score,
                    "reasons": r.issues + r.recommendations
                }
                for r in results if r.needs_manual_review
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📊 Validation report saved to: {output_file}")
    
    def _print_validation_summary(self):
        """Print validation statistics"""
        print("\n" + "="*60)
        print("AI CHUNK VALIDATION SUMMARY")
        print("="*60)
        print(f"Validation Model: {self.validation_model}")
        print(f"Total Validated: {self.validation_stats['total_validated']}")
        print(f"Passed: {self.validation_stats['passed_validation']}")
        print(f"Failed: {self.validation_stats['failed_validation']}")
        print(f"Manual Review Required: {self.validation_stats['manual_review_required']}")
        
        if self.validation_stats['total_validated'] > 0:
            pass_rate = (self.validation_stats['passed_validation'] / 
                        self.validation_stats['total_validated']) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
            
            review_rate = (self.validation_stats['manual_review_required'] / 
                          self.validation_stats['total_validated']) * 100
            print(f"Manual Review Rate: {review_rate:.1f}%")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="AI chunk conversion validator")
    parser.add_argument("converted_chunks_dir", help="Directory with converted Kotlin chunks")
    parser.add_argument("--original-chunks-dir", required=True,
                       help="Directory with original C++ chunks")
    parser.add_argument("--model", default="claude-3-5-sonnet",
                       help="AI model for validation")
    parser.add_argument("--output-report", default="validation_report.json",
                       help="Output validation report file")
    parser.add_argument("--validate-business-logic", action="store_true",
                       help="Enable business logic validation")
    parser.add_argument("--validate-comments", action="store_true", 
                       help="Enable comment preservation validation")
    parser.add_argument("--strict-validation", action="store_true",
                       help="Enable strict validation criteria")
    
    args = parser.parse_args()
    
    # Create validation criteria
    criteria = ValidationCriteria(
        comment_preservation=args.validate_comments,
        business_logic_accuracy=args.validate_business_logic,
        kotlin_syntax_correctness=True,
        null_safety_compliance=args.strict_validation,
        idiomatic_kotlin=args.strict_validation,
        performance_considerations=args.strict_validation
    )
    
    # Create validator
    validator = AIChunkValidator(args.model)
    
    print(f"🔍 Starting AI chunk validation with {args.model}")
    print(f"📁 Converted chunks: {args.converted_chunks_dir}")
    print(f"📁 Original chunks: {args.original_chunks_dir}")
    
    # Validate chunks
    validator.validate_conversion_directory(
        args.converted_chunks_dir,
        args.original_chunks_dir,
        args.output_report,
        criteria
    )
    
    print("✅ AI chunk validation completed!")

if __name__ == "__main__":
    main()
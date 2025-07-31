import json
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import openai
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables (optional)
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

@dataclass
class FitScoreResult:
    """Data class to hold fitscore calculation results"""
    total_score: float
    education_score: float
    career_trajectory_score: float
    company_relevance_score: float
    tenure_stability_score: float
    most_important_skills_score: float
    bonus_signals_score: float
    red_flags_penalty: float
    details: Dict[str, Any]
    recommendations: List[str]
    timestamp: str

class FitScoreCalculator:
    """
    Comprehensive FitScore Calculator implementing the detailed evaluation system
    with dynamic weights and company/role-specific adjustments.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the FitScore calculator"""
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not provided. Some features may be limited.")
        
        # Default weights (can be adjusted per company/role)
        self.default_weights = {
            "education": 0.20,
            "career_trajectory": 0.20,
            "company_relevance": 0.15,
            "tenure_stability": 0.15,
            "most_important_skills": 0.20,
            "bonus_signals": 0.05,
            "red_flags": -0.15  # Penalty
        }
        
        # Comprehensive elite schools database with specialty recognition
        self.tier1_schools = {
            "US_TOP15": [
                "MIT", "Stanford", "Harvard", "Berkeley", "CMU", "Caltech", 
                "Princeton", "Yale", "Columbia", "UPenn", "Cornell", 
                "University of Chicago", "Northwestern", "Johns Hopkins", "Brown"
            ],
            "ENGINEERING_CS_ELITE": [
                "University of Waterloo", "Georgia Tech", "UIUC", "UT Austin", 
                "UW Seattle", "Purdue", "Virginia Tech"
            ],
            "INTERNATIONAL_ELITE": [
                "Oxford", "Cambridge", "ETH Zurich", "University of Toronto", 
                "IIT", "Tsinghua", "Peking University", "National University of Singapore",
                "University of Melbourne", "KAIST", "Technion"
            ],
            "BUSINESS_ELITE": [
                "Wharton", "Harvard Business", "Stanford GSB", "Kellogg", "Booth", "Sloan"
            ],
            "MEDICAL_ELITE": [
                "Harvard Medical", "Johns Hopkins", "UCSF", "Mayo Clinic", 
                "Stanford Medical", "Penn Medical"
            ],
            "LAW_ELITE": [
                "Harvard Law", "Yale Law", "Stanford Law", "Columbia Law", 
                "NYU Law", "Chicago Law"
            ]
        }
        
        self.tier2_schools = {
            "STRONG_UNIVERSITIES": [
                "UCLA", "UCSD", "USC", "Michigan", "Wisconsin", "Washington",
                "North Carolina", "Virginia", "NYU", "Boston University",
                "Rice", "Vanderbilt", "Emory", "Georgetown", "Notre Dame",
                "Duke", "Dartmouth", "William & Mary", "Boston College"
            ],
            "ENGINEERING_STRONG": [
                "Texas A&M", "Penn State", "Ohio State", "Arizona State",
                "UC Irvine", "UC Davis", "Rutgers", "Maryland",
                "UC Santa Barbara", "UC Santa Cruz", "Northeastern",
                "RIT", "WPI", "RPI", "Stevens Tech", "Colorado School of Mines"
            ],
            "INTERNATIONAL_STRONG": [
                "McGill", "UBC", "Queen's", "London School of Economics", 
                "Imperial College", "University of Sydney", "ANU",
                "University of Hong Kong", "HKUST", "Sciences Po", "Bocconi"
            ]
        }
        
        # Specialty program recognition
        self.specialty_programs = {
            "CS_LEADERS": ["MIT", "Stanford", "CMU", "Berkeley", "Waterloo", "UIUC", "Georgia Tech", "UT Austin", "UW Seattle"],
            "ENGINEERING_LEADERS": ["MIT", "Stanford", "Berkeley", "Caltech", "CMU", "Georgia Tech", "Purdue", "Michigan", "UIUC"],
            "BUSINESS_MBA_LEADERS": ["Wharton", "Harvard", "Stanford", "Kellogg", "Booth", "Sloan", "Columbia", "Tuck"],
            "MEDICAL_LEADERS": ["Harvard Medical", "Johns Hopkins", "UCSF", "Mayo Clinic", "Stanford Medical"],
            "LAW_LEADERS": ["Harvard Law", "Yale Law", "Stanford Law", "Columbia Law", "NYU Law", "Chicago Law"]
        }
        
        # Elite companies database
        self.elite_companies = {
            "TECH_STARTUP_ELITE": [
                "Stripe", "Scale AI", "Databricks", "Canva", "Airbnb", "Uber",
                "Palantir", "Snowflake", "MongoDB", "Twilio"
            ],
            "TECH_ENTERPRISE_ELITE": [
                "Google", "Meta", "Apple", "Amazon", "Microsoft", "Netflix",
                "Salesforce", "Oracle", "SAP", "Adobe"
            ],
            "BIG4_ACCOUNTING": [
                "KPMG", "Deloitte", "EY", "PwC"
            ],
            "ELITE_LAW_FIRMS": [
                "Cravath", "Skadden", "Sullivan & Cromwell", "Wachtell",
                "Davis Polk", "Simpson Thacher"
            ],
            "ELITE_HEALTHCARE": [
                "Mayo Clinic", "Cleveland Clinic", "Johns Hopkins",
                "Massachusetts General", "UCSF Medical Center"
            ]
        }

    def calculate_fitscore(
        self, 
        resume_text: str, 
        job_description: str, 
        collateral: Optional[str] = None,
        company_weights: Optional[Dict[str, float]] = None,
        use_gpt4: bool = True
    ) -> FitScoreResult:
        """
        Calculate comprehensive fitscore using resume and job description with optional GPT-4 enhancement
        
        Args:
            resume_text: Candidate's resume text
            job_description: Job description text
            collateral: Optional additional information (company culture, specific requirements, etc.)
            company_weights: Optional custom weights for company/role
            use_gpt4: Whether to use GPT-4 for enhanced analysis (default: True)
            
        Returns:
            FitScoreResult with detailed scores and analysis
        """
        logger.info("Starting fitscore calculation with GPT-4 enhancement: %s", use_gpt4)
        
        # Step 1: Context Detection with GPT-4
        if use_gpt4 and self.client:
            context = self._detect_context_with_gpt4(job_description, resume_text)
            logger.info(f"Detected context: {context}")
        else:
            context = self._detect_context_fallback(job_description)
        
        # Step 2: Generate Smart Criteria with GPT-4
        if use_gpt4 and self.client:
            smart_criteria = self._generate_smart_criteria_with_gpt4(job_description, context)
            logger.info(f"Generated smart criteria: {smart_criteria}")
        else:
            smart_criteria = self._generate_smart_criteria_fallback(job_description, context)
        
        # Step 3: Dynamic Weight Adjustment with GPT-4
        if use_gpt4 and self.client:
            weights = self._adjust_weights_dynamically_with_gpt4(context, smart_criteria)
            # Remove reasoning from weights dict for calculation
            weights.pop('reasoning', None)
        else:
            weights = company_weights or self.default_weights
            if collateral:
                weights = self._adjust_weights_for_collateral(weights, collateral)
        
        # Step 4: Enhanced Skills Analysis with GPT-4
        if use_gpt4 and self.client:
            skills_analysis = self._extract_skills_with_gpt4(resume_text, job_description)
            logger.info(f"Enhanced skills analysis completed")
        else:
            skills_analysis = self._extract_skills_fallback(resume_text, job_description)
        
        # Step 5: Elite Evaluation against Smart Criteria with GPT-4
        if use_gpt4 and self.client:
            elite_evaluation = self._evaluate_against_smart_criteria_with_gpt4(resume_text, smart_criteria)
            logger.info(f"Elite evaluation completed")
        else:
            elite_evaluation = self._evaluate_against_smart_criteria_fallback(resume_text, smart_criteria)
        
        # Step 6: Traditional Component Evaluation (with GPT-4 enhancements where applicable)
        education_score, education_details = self._evaluate_education(resume_text, job_description)
        career_score, career_details = self._evaluate_career_trajectory(resume_text, job_description)
        company_score, company_details = self._evaluate_company_relevance(resume_text, job_description)
        tenure_score, tenure_details = self._evaluate_tenure_stability(resume_text, job_description)
        skills_score, skills_details = self._evaluate_most_important_skills(resume_text, job_description)
        bonus_score, bonus_details = self._evaluate_bonus_signals(resume_text, job_description)
        red_flags_penalty, red_flags_details = self._evaluate_red_flags(resume_text, job_description)
        
        # Step 7: Calculate weighted final score
        final_score = (
            education_score * weights["education"] +
            career_score * weights["career_trajectory"] +
            company_score * weights["company_relevance"] +
            tenure_score * weights["tenure_stability"] +
            skills_score * weights["most_important_skills"] +
            bonus_score * weights["bonus_signals"] +
            red_flags_penalty
        )
        
        # Step 8: Generate enhanced recommendations
        recommendations = self._generate_recommendations(
            final_score, education_score, career_score, company_score,
            tenure_score, skills_score, bonus_score, red_flags_penalty
        )
        
        # Step 9: Compile comprehensive results with GPT-4 insights
        details = {
            "education": education_details,
            "career_trajectory": career_details,
            "company_relevance": company_details,
            "tenure_stability": tenure_details,
            "most_important_skills": skills_details,
            "bonus_signals": bonus_details,
            "red_flags": red_flags_details,
            "weights_used": weights,
            "context_detection": context,
            "smart_criteria": smart_criteria,
            "skills_analysis": skills_analysis,
            "elite_evaluation": elite_evaluation,
            "gpt4_enhanced": use_gpt4 and self.client is not None
        }
        
        return FitScoreResult(
            total_score=final_score,
            education_score=education_score,
            career_trajectory_score=career_score,
            company_relevance_score=company_score,
            tenure_stability_score=tenure_score,
            most_important_skills_score=skills_score,
            bonus_signals_score=bonus_score,
            red_flags_penalty=red_flags_penalty,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )

    def _evaluate_education(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Evaluate education based on tier system (20% weight)"""
        logger.info("Evaluating education")
        
        # Extract education information
        education_info = self._extract_education_info(resume_text)
        
        total_score = 0.0
        education_details = {
            "institutions": [],
            "total_score": 0.0,
            "tier_breakdown": {},
            "strengths": [],
            "concerns": []
        }
        
        for edu in education_info:
            institution_score = self._score_institution(edu["institution"], edu["degree_type"], edu["field"])
            total_score += institution_score
            
            education_details["institutions"].append({
                "institution": edu["institution"],
                "degree": edu["degree_type"],
                "field": edu["field"],
                "score": institution_score,
                "tier": self._get_institution_tier(edu["institution"])
            })
        
        # Calculate average score
        if education_info:
            avg_score = total_score / len(education_info)
        else:
            avg_score = 1.0  # Minimum score for no education
            education_details["concerns"].append("No education information found")
        
        # Apply graduate degree boost
        graduate_degrees = [edu for edu in education_info if "master" in edu["degree_type"].lower() or "phd" in edu["degree_type"].lower()]
        if graduate_degrees:
            avg_score = min(10.0, avg_score + 1.0)  # Boost for graduate degrees
            education_details["strengths"].append("Graduate degree(s) present")
        
        education_details["total_score"] = avg_score
        education_details["tier"] = self._get_institution_tier(education_info[0]["institution"]) if education_info else "No Education"
        
        return avg_score, education_details

    def _evaluate_career_trajectory(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Evaluate career trajectory and progression using detailed scoring (20% weight)"""
        logger.info("Evaluating career trajectory")
        
        # Extract work experience
        work_experience = self._extract_work_experience(resume_text)
        
        if not work_experience:
            return 1.0, {"error": "No work experience found", "score": 1.0}
        
        # Sort by date (most recent first)
        work_experience.sort(key=lambda x: x.get("end_date", "Present"), reverse=True)
        
        trajectory_details = {
            "positions": [],
            "progression_pattern": "",
            "leadership_roles": 0,
            "scope_increases": 0,
            "ownership_indicators": 0,
            "complexity_growth": 0,
            "score": 0.0,
            "progression_level": ""
        }
        
        # Analyze each position for progression indicators
        position_scores = []
        total_leadership = 0
        total_scope = 0
        total_ownership = 0
        total_complexity = 0
        
        for i, position in enumerate(work_experience):
            title = position["title"]
            description = position.get("description", "")
            
            # Base title score
            title_score = self._score_job_title(title)
            
            # Leadership indicators
            leadership_score = 0.0
            if any(word in title.lower() for word in ["manager", "director", "lead", "head", "chief", "vp", "cto", "ceo", "principal", "staff"]):
                leadership_score = 2.0
                total_leadership += 1
            
            # Scope and responsibility indicators
            scope_score = 0.0
            if any(word in description.lower() for word in ["team", "budget", "revenue", "strategy", "architect", "cross-functional", "stakeholder"]):
                scope_score = 1.5
                total_scope += 1
            
            # Ownership indicators
            ownership_score = 0.0
            if any(word in description.lower() for word in ["owned", "led", "managed", "responsible for", "delivered", "launched", "improved"]):
                ownership_score = 1.0
                total_ownership += 1
            
            # Complexity indicators
            complexity_score = 0.0
            if any(word in description.lower() for word in ["scalable", "distributed", "microservices", "architecture", "system design", "technical leadership"]):
                complexity_score = 1.0
                total_complexity += 1
            
            position_score = title_score + leadership_score + scope_score + ownership_score + complexity_score
            position_scores.append(position_score)
            
            trajectory_details["positions"].append({
                "title": title,
                "company": position["company"],
                "duration": position.get("duration", ""),
                "score": position_score,
                "leadership": leadership_score > 0,
                "scope": scope_score > 0,
                "ownership": ownership_score > 0,
                "complexity": complexity_score > 0
            })
        
        # Calculate progression metrics
        avg_position_score = sum(position_scores) / len(position_scores)
        
        # Analyze progression pattern
        if len(position_scores) >= 3:
            recent_scores = position_scores[:3]
            
            # Check for exceptional progression (9.5-10.0)
            if (recent_scores[0] >= 9.0 and recent_scores[1] >= 8.0 and 
                total_leadership >= 2 and total_ownership >= 2):
                progression_score = 9.5
                trajectory_details["progression_pattern"] = "Exceptional progression with leadership and ownership"
                trajectory_details["progression_level"] = "Exceptional (9.5-10.0)"
            
            # Check for clear upward progression (9.0-9.4)
            elif (recent_scores[0] > recent_scores[1] > recent_scores[2] and 
                  recent_scores[0] >= 7.5 and total_leadership >= 1):
                progression_score = 9.0
                trajectory_details["progression_pattern"] = "Clear upward progression with leadership"
                trajectory_details["progression_level"] = "Clear Upward (9.0-9.4)"
            
            # Check for strong progression (8.0-8.9)
            elif (recent_scores[0] > recent_scores[2] and 
                  recent_scores[0] >= 7.0 and total_scope >= 1):
                progression_score = 8.0
                trajectory_details["progression_pattern"] = "Strong progression with scope growth"
                trajectory_details["progression_level"] = "Strong (8.0-8.9)"
            
            # Check for good progression (7.0-7.9)
            elif recent_scores[0] >= 6.0 and total_ownership >= 1:
                progression_score = 7.0
                trajectory_details["progression_pattern"] = "Good progression with ownership"
                trajectory_details["progression_level"] = "Good (7.0-7.9)"
            
            # Check for steady progression (6.0-6.9)
            elif recent_scores[0] >= 5.0:
                progression_score = 6.0
                trajectory_details["progression_pattern"] = "Steady progression"
                trajectory_details["progression_level"] = "Steady (6.0-6.9)"
            
            # Limited progression (4.0-5.9)
            elif recent_scores[0] >= 4.0:
                progression_score = 4.0
                trajectory_details["progression_pattern"] = "Limited progression"
                trajectory_details["progression_level"] = "Limited (4.0-5.9)"
            
            # No progression (1.0-3.9)
            else:
                progression_score = 1.0
                trajectory_details["progression_pattern"] = "No clear progression"
                trajectory_details["progression_level"] = "No Progression (1.0-3.9)"
        
        else:
            # For candidates with fewer positions, base on current level
            if avg_position_score >= 8.0:
                progression_score = 8.0
            elif avg_position_score >= 6.0:
                progression_score = 6.0
            else:
                progression_score = 4.0
        
        # Update details
        trajectory_details["leadership_roles"] = total_leadership
        trajectory_details["scope_increases"] = total_scope
        trajectory_details["ownership_indicators"] = total_ownership
        trajectory_details["complexity_growth"] = total_complexity
        trajectory_details["score"] = progression_score
        
        return progression_score, trajectory_details

    def _evaluate_company_relevance(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Evaluate company relevance based on role type (15% weight)"""
        logger.info("Evaluating company relevance")
        
        work_experience = self._extract_work_experience(resume_text)
        role_type = self._detect_role_type(job_description)
        company_type = self._detect_company_type(job_description)
        
        company_details = {
            "role_type": role_type,
            "target_company_type": company_type,
            "companies": [],
            "relevance_score": 0.0
        }
        
        if not work_experience:
            return 1.0, {"error": "No work experience found", "score": 1.0}
        
        total_relevance = 0.0
        
        for position in work_experience:
            company_score = self._score_company_relevance(
                position["company"], 
                role_type, 
                company_type
            )
            total_relevance += company_score
            
            company_details["companies"].append({
                "company": position["company"],
                "role": position["title"],
                "relevance_score": company_score
            })
        
        avg_relevance = total_relevance / len(work_experience)
        company_details["relevance_score"] = avg_relevance
        
        return avg_relevance, company_details

    def _evaluate_tenure_stability(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Evaluate tenure and stability using detailed scoring rules (15% weight)"""
        logger.info("Evaluating tenure stability")
        
        work_experience = self._extract_work_experience(resume_text)
        
        if not work_experience:
            return 1.0, {"error": "No work experience found", "score": 1.0}
        
        tenure_details = {
            "positions": [],
            "average_tenure": 0.0,
            "tenure_pattern": "",
            "stability_score": 0.0,
            "excluded_positions": [],
            "internship_count": 0,
            "elite_company_tenure": 0.0,
            "tenure_level": ""
        }
        
        total_tenure = 0.0
        valid_positions = 0
        internship_count = 0
        elite_company_tenure = 0.0
        
        # Identify elite companies for tenure bonus
        elite_companies = []
        for category, companies in self.elite_companies.items():
            elite_companies.extend(companies)
        
        for position in work_experience:
            title = position["title"].lower()
            company = position["company"]
            
            # CRITICAL: Exclude internships, co-ops, and part-time student work
            if any(word in title for word in ["intern", "internship", "co-op", "coop", "part-time", "parttime"]):
                tenure_details["excluded_positions"].append({
                    "position": position["title"],
                    "company": position["company"],
                    "reason": "Internship/Co-op/Part-time (excluded from tenure calculation)"
                })
                internship_count += 1
                continue
            
            # Only count full-time positions post-graduation
            tenure_years = self._calculate_tenure_years(position.get("duration", ""))
            if tenure_years > 0:
                total_tenure += tenure_years
                valid_positions += 1
                
                # Check if it's an elite company for tenure bonus
                is_elite = any(elite_company.lower() in company.lower() for elite_company in elite_companies)
                if is_elite:
                    elite_company_tenure += tenure_years
                
                tenure_details["positions"].append({
                    "company": position["company"],
                    "title": position["title"],
                    "tenure_years": tenure_years,
                    "is_elite_company": is_elite
                })
        
        if valid_positions == 0:
            return 1.0, {"error": "No valid full-time positions found", "score": 1.0}
        
        avg_tenure = total_tenure / valid_positions
        tenure_details["average_tenure"] = avg_tenure
        tenure_details["internship_count"] = internship_count
        tenure_details["elite_company_tenure"] = elite_company_tenure
        
        # Apply detailed tenure scoring with decimals for precision
        if avg_tenure >= 3.0:
            stability_score = 9.5
            tenure_details["tenure_pattern"] = "Elite stability (3+ years average)"
            tenure_details["tenure_level"] = "Elite (9.5-10.0)"
        elif avg_tenure >= 2.5:
            stability_score = 8.5
            tenure_details["tenure_pattern"] = "Strong stability (2.5-3 years average)"
            tenure_details["tenure_level"] = "Strong (8.5-9.4)"
        elif avg_tenure >= 2.0:
            stability_score = 7.5
            tenure_details["tenure_pattern"] = "Good stability (2-2.5 years average)"
            tenure_details["tenure_level"] = "Good (7.5-8.4)"
        elif avg_tenure >= 1.5:
            stability_score = 6.5
            tenure_details["tenure_pattern"] = "Reasonable stability (1.5-2 years average)"
            tenure_details["tenure_level"] = "Reasonable (6.5-7.4)"
        elif avg_tenure >= 1.0:
            stability_score = 5.5
            tenure_details["tenure_pattern"] = "Some job hopping (1-1.5 years average)"
            tenure_details["tenure_level"] = "Some Hopping (5.5-6.4)"
        elif avg_tenure >= 0.5:
            stability_score = 4.0
            tenure_details["tenure_pattern"] = "Frequent job changes (0.5-1 year average)"
            tenure_details["tenure_level"] = "Frequent Changes (4.0-5.4)"
        else:
            stability_score = 1.0
            tenure_details["tenure_pattern"] = "Very short tenures (less than 0.5 years average)"
            tenure_details["tenure_level"] = "Very Short (1.0-3.9)"
        
        # Apply elite company tenure bonus
        if elite_company_tenure > 0:
            elite_bonus = min(0.5, elite_company_tenure * 0.1)  # Max 0.5 bonus
            stability_score = min(10.0, stability_score + elite_bonus)
            tenure_details["elite_tenure_bonus"] = elite_bonus
        
        # Apply internship excellence bonus (3-4 quality internships)
        if internship_count >= 3:
            internship_bonus = 0.3
            stability_score = min(10.0, stability_score + internship_bonus)
            tenure_details["internship_bonus"] = internship_bonus
        
        tenure_details["stability_score"] = stability_score
        return stability_score, tenure_details

    def _evaluate_most_important_skills(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Evaluate most important skills match (20% weight)"""
        logger.info("Evaluating skills match")
        
        # Extract required skills from job description
        required_skills = self._extract_required_skills(job_description)
        
        # Extract candidate skills from resume
        candidate_skills = self._extract_candidate_skills(resume_text)
        
        skills_details = {
            "required_skills": required_skills,
            "candidate_skills": candidate_skills,
            "matches": [],
            "missing": [],
            "match_percentage": 0.0,
            "score": 0.0
        }
        
        if not required_skills:
            return 5.0, {"error": "No required skills identified", "score": 5.0}
        
        matches = []
        missing = []
        
        for skill in required_skills:
            if self._skill_matches(skill, candidate_skills):
                matches.append(skill)
            else:
                missing.append(skill)
        
        match_percentage = len(matches) / len(required_skills) * 100
        
        # Score based on match percentage
        if match_percentage >= 90:
            skills_score = 9.0
        elif match_percentage >= 80:
            skills_score = 7.5
        elif match_percentage >= 70:
            skills_score = 6.0
        elif match_percentage >= 50:
            skills_score = 4.0
        else:
            skills_score = 1.0
        
        skills_details["matches"] = matches
        skills_details["missing"] = missing
        skills_details["match_percentage"] = match_percentage
        skills_details["score"] = skills_score
        
        return skills_score, skills_details

    def _evaluate_bonus_signals(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Evaluate bonus signals (5% weight)"""
        logger.info("Evaluating bonus signals")
        
        bonus_details = {
            "signals_found": [],
            "total_score": 0.0
        }
        
        bonus_score = 0.0
        
        # Check for exceptional signals (5 points)
        exceptional_signals = [
            "patent", "published", "forbes", "founder", "board", "olympic",
            "military", "ted talk", "book", "award", "media coverage"
        ]
        
        for signal in exceptional_signals:
            if signal in resume_text.lower():
                bonus_score += 5.0
                bonus_details["signals_found"].append(f"Exceptional: {signal}")
        
        # Check for strong signals (3-4 points)
        strong_signals = [
            "open source", "speaking", "teaching", "certification",
            "hackathon", "leadership", "volunteer", "side project"
        ]
        
        for signal in strong_signals:
            if signal in resume_text.lower():
                bonus_score += 3.0
                bonus_details["signals_found"].append(f"Strong: {signal}")
        
        # Check for some signals (1-2 points)
        some_signals = [
            "portfolio", "community", "course", "competition", "language"
        ]
        
        for signal in some_signals:
            if signal in resume_text.lower():
                bonus_score += 1.0
                bonus_details["signals_found"].append(f"Some: {signal}")
        
        # Cap bonus score at 5.0
        final_bonus_score = min(5.0, bonus_score)
        bonus_details["total_score"] = final_bonus_score
        
        return final_bonus_score, bonus_details

    def _evaluate_red_flags(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Evaluate red flags (-15% penalty)"""
        logger.info("Evaluating red flags")
        
        red_flags_details = {
            "flags_found": [],
            "penalty": 0.0
        }
        
        penalty = 0.0
        
        # Check for major red flags (-15 points)
        major_flags = [
            "falsified", "plagiarized", "criminal", "ethical violation",
            "diploma mill", "unaccredited"
        ]
        
        for flag in major_flags:
            if flag in resume_text.lower():
                penalty -= 15.0
                red_flags_details["flags_found"].append(f"Major: {flag}")
        
        # Check for moderate red flags (-10 points)
        moderate_flags = [
            "job hopping", "employment gap", "no progression",
            "short tenure", "concerning pattern"
        ]
        
        for flag in moderate_flags:
            if flag in resume_text.lower():
                penalty -= 10.0
                red_flags_details["flags_found"].append(f"Moderate: {flag}")
        
        # Check for minor red flags (-5 points)
        minor_flags = [
            "overqualified", "location mismatch", "missing certification"
        ]
        
        for flag in minor_flags:
            if flag in resume_text.lower():
                penalty -= 5.0
                red_flags_details["flags_found"].append(f"Minor: {flag}")
        
        red_flags_details["penalty"] = penalty
        return penalty, red_flags_details

    def _generate_recommendations(
        self, 
        final_score: float,
        education_score: float,
        career_score: float,
        company_score: float,
        tenure_score: float,
        skills_score: float,
        bonus_score: float,
        red_flags_penalty: float
    ) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        if final_score >= 8.2:
            recommendations.append("SUBMITTABLE CANDIDATE - Recommend to submit")
        else:
            recommendations.append("RECOMMENDED REJECT - Below elite hiring bar")
        
        if education_score < 6.0:
            recommendations.append("Education concerns - consider program strength and relevance")
        
        if career_score < 6.0:
            recommendations.append("Career trajectory concerns - limited progression visible")
        
        if company_score < 6.0:
            recommendations.append("Company relevance concerns - may not fit target environment")
        
        if tenure_score < 6.0:
            recommendations.append("Tenure stability concerns - frequent job changes")
        
        if skills_score < 6.0:
            recommendations.append("Skills gap - missing critical capabilities")
        
        if red_flags_penalty < -5.0:
            recommendations.append("Red flags detected - requires careful review")
        
        return recommendations

    # Helper methods for data extraction and scoring
    
    def _extract_education_info(self, resume_text: str) -> List[Dict]:
        """Extract education information from resume"""
        education_info = []
        
        # Simple regex patterns for education extraction
        education_patterns = [
            r"([A-Z][a-zA-Z\s&]+(?:University|College|Institute|School))",
            r"(Bachelor|Master|PhD|MBA|MS|BS|BA)\s+(?:of|in)?\s+([A-Za-z\s]+)",
        ]
        
        # Extract basic education info
        for pattern in education_patterns:
            matches = re.finditer(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                education_info.append({
                    "institution": match.group(1) if match.group(1) else "Unknown",
                    "degree_type": match.group(2) if len(match.groups()) > 1 else "Unknown",
                    "field": "General" if len(match.groups()) <= 1 else match.group(2)
                })
        
        return education_info

    def _extract_work_experience(self, resume_text: str) -> List[Dict]:
        """Extract work experience from resume with improved parsing"""
        work_experience = []
        
        # Enhanced patterns to extract job information
        # Look for patterns like "Senior Software Engineer\nGoogle Inc.\n2021-2024 (3 years)"
        lines = resume_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for job titles
            if any(title in line.lower() for title in ['engineer', 'manager', 'director', 'analyst', 'developer', 'consultant', 'lead', 'senior', 'principal', 'staff']):
                title = line
                company = "Unknown Company"
                duration = "Unknown"
                description = ""
                
                # Look for company name in next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not any(skip in next_line.lower() for skip in ['experience', 'education', 'skills', 'bonus']):
                        # Check if it looks like a company name
                        if any(company_indicator in next_line.lower() for company_indicator in ['inc', 'corp', 'llc', 'ltd', 'company', 'google', 'microsoft', 'amazon', 'apple', 'meta', 'ibm', 'oracle']):
                            company = next_line
                            break
                
                # Look for duration in the same area
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if re.search(r'\d{4}-\d{4}|\(\d+\s+years?\)|\(\d+\s+months?\)', next_line):
                        duration = next_line
                        break
                
                # Collect description from subsequent lines
                desc_lines = []
                for j in range(i+1, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('-') or next_line.startswith('•'):
                        desc_lines.append(next_line)
                    elif next_line and not any(skip in next_line.lower() for skip in ['experience', 'education', 'skills', 'bonus']):
                        break
                description = ' '.join(desc_lines)
                
                work_experience.append({
                    "title": title,
                    "company": company,
                    "duration": duration,
                    "description": description
                })
        
        return work_experience

    def _score_institution(self, institution: str, degree_type: str, field: str) -> float:
        """Score an educational institution based on comprehensive tier classification"""
        institution_lower = institution.lower()
        
        # Check Tier 1 schools with specialty recognition
        for category, schools in self.tier1_schools.items():
            for school in schools:
                if school.lower() in institution_lower:
                    base_score = 9.5
                    
                    # Apply specialty program bonuses
                    if field and self._is_specialty_match(field, category):
                        base_score = min(10.0, base_score + 0.5)
                    
                    # Graduate degree boost
                    if degree_type and ("master" in degree_type.lower() or "phd" in degree_type.lower()):
                        base_score = min(10.0, base_score + 0.3)
                    
                    return base_score
        
        # Check Tier 2 schools
        for category, schools in self.tier2_schools.items():
            for school in schools:
                if school.lower() in institution_lower:
                    base_score = 7.5
                    
                    # Apply specialty program bonuses
                    if field and self._is_specialty_match(field, category):
                        base_score = min(8.5, base_score + 0.5)
                    
                    # Graduate degree boost
                    if degree_type and ("master" in degree_type.lower() or "phd" in degree_type.lower()):
                        base_score = min(8.5, base_score + 0.3)
                    
                    return base_score
        
        # Check specialty programs for non-tier schools
        for specialty, schools in self.specialty_programs.items():
            for school in schools:
                if school.lower() in institution_lower and field and self._is_specialty_match(field, specialty):
                    return 8.0
        
        # Default scoring for other institutions
        if "university" in institution_lower or "college" in institution_lower:
            base_score = 5.0
            # Graduate degree boost for any institution
            if degree_type and ("master" in degree_type.lower() or "phd" in degree_type.lower()):
                base_score = min(6.5, base_score + 0.5)
            return base_score
        else:
            return 3.0
    
    def _is_specialty_match(self, field: str, category: str) -> bool:
        """Check if field of study matches specialty category"""
        field_lower = field.lower()
        
        if "CS" in category or "COMPUTER" in category:
            return any(term in field_lower for term in ["computer", "software", "cs", "computing"])
        elif "ENGINEERING" in category:
            return any(term in field_lower for term in ["engineering", "mechanical", "electrical", "civil", "chemical"])
        elif "BUSINESS" in category or "MBA" in category:
            return any(term in field_lower for term in ["business", "mba", "management", "finance", "economics"])
        elif "MEDICAL" in category:
            return any(term in field_lower for term in ["medical", "medicine", "health", "nursing", "pharmacy"])
        elif "LAW" in category:
            return any(term in field_lower for term in ["law", "legal", "juris", "jd"])
        
        return False

    def _get_institution_tier(self, institution: str) -> str:
        """Get institution tier classification"""
        institution_lower = institution.lower()
        
        # Check Tier 1 schools
        for category, schools in self.tier1_schools.items():
            for school in schools:
                if school.lower() in institution_lower:
                    return f"Tier 1 - {category.replace('_', ' ').title()}"
        
        # Check Tier 2 schools
        for category, schools in self.tier2_schools.items():
            for school in schools:
                if school.lower() in institution_lower:
                    return f"Tier 2 - {category.replace('_', ' ').title()}"
        
        # Check specialty programs
        for specialty, schools in self.specialty_programs.items():
            for school in schools:
                if school.lower() in institution_lower:
                    return f"Specialty - {specialty.replace('_', ' ').title()}"
        
        return "Tier 3"

    def _score_job_title(self, title: str) -> float:
        """Score job title based on seniority"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["ceo", "cto", "cfo", "vp", "director"]):
            return 9.0
        elif any(word in title_lower for word in ["senior", "lead", "principal"]):
            return 7.0
        elif any(word in title_lower for word in ["manager", "supervisor"]):
            return 6.0
        elif any(word in title_lower for word in ["engineer", "analyst", "developer"]):
            return 5.0
        else:
            return 3.0

    def _detect_role_type(self, job_description: str) -> str:
        """Detect role type from job description"""
        jd_lower = job_description.lower()
        
        if any(word in jd_lower for word in ["software", "engineer", "developer", "programmer"]):
            return "technical"
        elif any(word in jd_lower for word in ["manager", "director", "lead"]):
            return "management"
        elif any(word in jd_lower for word in ["sales", "account", "business"]):
            return "sales"
        elif any(word in jd_lower for word in ["legal", "attorney", "law"]):
            return "legal"
        elif any(word in jd_lower for word in ["accounting", "cpa", "audit"]):
            return "accounting"
        elif any(word in jd_lower for word in ["healthcare", "medical", "nurse"]):
            return "healthcare"
        else:
            return "general"

    def _detect_company_type(self, job_description: str) -> str:
        """Detect company type from job description"""
        jd_lower = job_description.lower()
        
        if any(word in jd_lower for word in ["startup", "seed", "series", "early-stage"]):
            return "startup"
        elif any(word in jd_lower for word in ["enterprise", "fortune", "large company"]):
            return "enterprise"
        elif any(word in jd_lower for word in ["law firm", "legal"]):
            return "law_firm"
        elif any(word in jd_lower for word in ["accounting", "cpa"]):
            return "accounting"
        elif any(word in jd_lower for word in ["healthcare", "hospital"]):
            return "healthcare"
        else:
            return "general"

    def _score_company_relevance(self, company: str, role_type: str, company_type: str) -> float:
        """Score company relevance based on role and company type"""
        company_lower = company.lower()
        
        if role_type == "technical":
            if company_type == "startup":
                for elite_startup in self.elite_companies["TECH_STARTUP_ELITE"]:
                    if elite_startup.lower() in company_lower:
                        return 9.0
            elif company_type == "enterprise":
                for elite_enterprise in self.elite_companies["TECH_ENTERPRISE_ELITE"]:
                    if elite_enterprise.lower() in company_lower:
                        return 9.0
        
        elif role_type == "accounting":
            for big4 in self.elite_companies["BIG4_ACCOUNTING"]:
                if big4.lower() in company_lower:
                    return 9.0
        
        elif role_type == "legal":
            for elite_law in self.elite_companies["ELITE_LAW_FIRMS"]:
                if elite_law.lower() in company_lower:
                    return 9.0
        
        elif role_type == "healthcare":
            for elite_healthcare in self.elite_companies["ELITE_HEALTHCARE"]:
                if elite_healthcare.lower() in company_lower:
                    return 9.0
        
        # Default score
        return 5.0

    def _calculate_tenure_years(self, duration: str) -> float:
        """Calculate tenure in years from duration string with improved parsing"""
        if not duration or duration == "Unknown":
            return 0.0
        
        duration_lower = duration.lower()
        
        # Pattern 1: "2021-2024 (3 years)"
        years_match = re.search(r'\((\d+(?:\.\d+)?)\s+years?\)', duration_lower)
        if years_match:
            return float(years_match.group(1))
        
        # Pattern 2: "2021-2024" - calculate years
        year_range_match = re.search(r'(\d{4})-(\d{4})', duration)
        if year_range_match:
            start_year = int(year_range_match.group(1))
            end_year = int(year_range_match.group(2))
            return end_year - start_year
        
        # Pattern 3: "3 years" or "2.5 years"
        years_only_match = re.search(r'(\d+(?:\.\d+)?)\s+years?', duration_lower)
        if years_only_match:
            return float(years_only_match.group(1))
        
        # Pattern 4: "6 months" - convert to years
        months_match = re.search(r'(\d+)\s+months?', duration_lower)
        if months_match:
            months = int(months_match.group(1))
            return months / 12.0
        
        # Pattern 5: Just a number (assume years)
        number_match = re.search(r'^(\d+(?:\.\d+)?)$', duration.strip())
        if number_match:
            return float(number_match.group(1))
        
        return 1.0  # Default to 1 year if can't parse

    def _extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description"""
        skills = []
        
        # Comprehensive technical skills database
        tech_skills = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "php", "ruby", "swift", "kotlin", "scala",
            
            # Web Technologies
            "react", "vue", "angular", "node.js", "express", "django", "flask", "spring", "laravel", "asp.net",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github", "terraform", "ansible",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra",
            
            # Data & AI
            "machine learning", "ai", "data science", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spark", "hadoop",
            
            # Mobile & Desktop
            "ios", "android", "react native", "flutter", "xamarin", "electron",
            
            # Other Technologies
            "graphql", "rest api", "microservices", "serverless", "blockchain", "cybersecurity", "devops", "sre"
        ]
        
        jd_lower = job_description.lower()
        for skill in tech_skills:
            if skill in jd_lower:
                skills.append(skill)
        
        return skills

    def _extract_candidate_skills(self, resume_text: str) -> List[str]:
        """Extract candidate skills from resume"""
        skills = []
        
        # Comprehensive technical skills database (same as required skills)
        tech_skills = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "php", "ruby", "swift", "kotlin", "scala",
            
            # Web Technologies
            "react", "vue", "angular", "node.js", "express", "django", "flask", "spring", "laravel", "asp.net",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github", "terraform", "ansible",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra",
            
            # Data & AI
            "machine learning", "ai", "data science", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spark", "hadoop",
            
            # Mobile & Desktop
            "ios", "android", "react native", "flutter", "xamarin", "electron",
            
            # Other Technologies
            "graphql", "rest api", "microservices", "serverless", "blockchain", "cybersecurity", "devops", "sre"
        ]
        
        resume_lower = resume_text.lower()
        for skill in tech_skills:
            if skill in resume_lower:
                skills.append(skill)
        
        return skills

    def _skill_matches(self, required_skill: str, candidate_skills: List[str]) -> bool:
        """Check if candidate has required skill"""
        return required_skill.lower() in [skill.lower() for skill in candidate_skills]

    def _adjust_weights_for_collateral(self, weights: Dict[str, float], collateral: str) -> Dict[str, float]:
        """Adjust weights based on collateral information"""
        adjusted_weights = weights.copy()
        collateral_lower = collateral.lower()
        
        # Adjust weights based on collateral content
        if "startup" in collateral_lower or "early-stage" in collateral_lower:
            # Startups may value skills and company relevance more
            adjusted_weights["most_important_skills"] += 0.05
            adjusted_weights["company_relevance"] += 0.05
            adjusted_weights["education"] -= 0.05
            adjusted_weights["tenure_stability"] -= 0.05
        
        elif "enterprise" in collateral_lower or "large company" in collateral_lower:
            # Enterprises may value education and stability more
            adjusted_weights["education"] += 0.05
            adjusted_weights["tenure_stability"] += 0.05
            adjusted_weights["most_important_skills"] -= 0.05
            adjusted_weights["company_relevance"] -= 0.05
        
        elif "leadership" in collateral_lower or "management" in collateral_lower:
            # Leadership roles may value career trajectory more
            adjusted_weights["career_trajectory"] += 0.05
            adjusted_weights["bonus_signals"] += 0.02
            adjusted_weights["most_important_skills"] -= 0.07
        
        # Normalize weights to ensure they sum to 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight != 1.0:
            for key in adjusted_weights:
                if key != "red_flags":  # Don't normalize penalty
                    adjusted_weights[key] = adjusted_weights[key] / total_weight
        
        return adjusted_weights

    def to_dict(self, result: FitScoreResult) -> Dict:
        """Convert FitScoreResult to dictionary"""
        return {
            "total_score": result.total_score,
            "education_score": result.education_score,
            "career_trajectory_score": result.career_trajectory_score,
            "company_relevance_score": result.company_relevance_score,
            "tenure_stability_score": result.tenure_stability_score,
            "most_important_skills_score": result.most_important_skills_score,
            "bonus_signals_score": result.bonus_signals_score,
            "red_flags_penalty": result.red_flags_penalty,
            "details": result.details,
            "recommendations": result.recommendations,
            "timestamp": result.timestamp,
            "submittable": result.total_score >= 8.2
        }

    def to_json(self, result: FitScoreResult) -> str:
        """Convert FitScoreResult to JSON string"""
        return json.dumps(self.to_dict(result), indent=2)

    def _detect_context_with_gpt4(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """
        Use GPT-4 to intelligently detect context, industry, role type, and company type
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback context detection")
            return self._detect_context_fallback(job_description)
        
        try:
            prompt = f"""
            Analyze the following job description and resume to detect:
            1. Industry (tech, healthcare, law, finance, etc.)
            2. Company type (startup, enterprise, law firm, accounting, healthcare, etc.)
            3. Role type (technical, management, sales, legal, accounting, healthcare, etc.)
            4. Role level (entry, mid, senior, executive)
            5. Key requirements and preferences
            
            Job Description:
            {job_description}
            
            Resume:
            {resume_text}
            
            Return a JSON object with:
            {{
                "industry": "detected industry",
                "company_type": "startup|enterprise|law_firm|accounting|healthcare|consulting|financial|academic|government|non_profit",
                "role_type": "technical|management|sales|legal|accounting|healthcare|consulting|financial|academic|government|non_profit",
                "role_level": "entry|mid|senior|executive",
                "key_requirements": ["requirement1", "requirement2"],
                "preferences": ["preference1", "preference2"],
                "company_size": "small|medium|large",
                "growth_stage": "seed|series_a|series_b|series_c|established|public"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            context_data = json.loads(response.choices[0].message.content)
            logger.info(f"GPT-4 detected context: {context_data}")
            return context_data
            
        except Exception as e:
            logger.error(f"GPT-4 context detection failed: {e}")
            return self._detect_context_fallback(job_description)

    def _generate_smart_criteria_with_gpt4(self, job_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GPT-4 to generate elite hiring criteria based on job description and context
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback criteria")
            return self._generate_smart_criteria_fallback(job_description, context)
        
        try:
            prompt = f"""
            Based on the job description and context, generate elite hiring criteria for top 1-2% performers.
            
            Context: {json.dumps(context, indent=2)}
            
            Job Description:
            {job_description}
            
            Generate elite criteria in JSON format:
            {{
                "mission_critical_skills": [
                    {{
                        "skill": "skill name",
                        "description": "what they must be able to do",
                        "importance": "critical|high|medium"
                    }}
                ],
                "elite_company_benchmarks": [
                    "company1",
                    "company2"
                ],
                "expected_outcomes": [
                    "outcome1",
                    "outcome2"
                ],
                "domain_mastery_requirements": [
                    "requirement1",
                    "requirement2"
                ],
                "leadership_indicators": [
                    "indicator1",
                    "indicator2"
                ],
                "technical_complexity": "low|medium|high",
                "scale_requirements": "small|medium|large",
                "industry_specific_requirements": [
                    "requirement1",
                    "requirement2"
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            criteria = json.loads(response.choices[0].message.content)
            logger.info(f"GPT-4 generated smart criteria: {criteria}")
            return criteria
            
        except Exception as e:
            logger.error(f"GPT-4 criteria generation failed: {e}")
            return self._generate_smart_criteria_fallback(job_description, context)

    def _extract_skills_with_gpt4(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Use GPT-4 to extract and match skills more intelligently
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback skills extraction")
            return self._extract_skills_fallback(resume_text, job_description)
        
        try:
            prompt = f"""
            Extract and analyze skills from the resume and job description.
            
            Resume:
            {resume_text}
            
            Job Description:
            {job_description}
            
            Return JSON with:
            {{
                "candidate_skills": [
                    {{
                        "skill": "skill name",
                        "evidence": "where/how it's mentioned",
                        "proficiency": "basic|intermediate|advanced|expert",
                        "years_experience": "estimated years"
                    }}
                ],
                "required_skills": [
                    {{
                        "skill": "skill name",
                        "importance": "required|preferred|nice_to_have",
                        "description": "what they need to do with it"
                    }}
                ],
                "skill_matches": [
                    {{
                        "skill": "skill name",
                        "match_quality": "exact|partial|inferred|missing",
                        "candidate_evidence": "how candidate demonstrates it",
                        "requirement_level": "what job requires"
                    }}
                ],
                "missing_critical_skills": ["skill1", "skill2"],
                "inferred_skills": [
                    {{
                        "skill": "skill name",
                        "reasoning": "why we can infer this",
                        "confidence": "high|medium|low"
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            skills_analysis = json.loads(response.choices[0].message.content)
            logger.info(f"GPT-4 skills analysis completed")
            return skills_analysis
            
        except Exception as e:
            logger.error(f"GPT-4 skills extraction failed: {e}")
            return self._extract_skills_fallback(resume_text, job_description)

    def _evaluate_against_smart_criteria_with_gpt4(self, resume_text: str, smart_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GPT-4 to evaluate candidate against elite smart criteria
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback evaluation")
            return self._evaluate_against_smart_criteria_fallback(resume_text, smart_criteria)
        
        try:
            prompt = f"""
            Evaluate the candidate against elite hiring criteria.
            
            Resume:
            {resume_text}
            
            Elite Criteria:
            {json.dumps(smart_criteria, indent=2)}
            
            Return evaluation in JSON:
            {{
                "mission_critical_skills_score": {{
                    "score": 0-10,
                    "matches": ["skill1", "skill2"],
                    "gaps": ["skill1", "skill2"],
                    "reasoning": "detailed explanation"
                }},
                "elite_company_benchmark_score": {{
                    "score": 0-10,
                    "company_matches": ["company1", "company2"],
                    "reasoning": "explanation"
                }},
                "expected_outcomes_score": {{
                    "score": 0-10,
                    "outcomes_demonstrated": ["outcome1", "outcome2"],
                    "missing_outcomes": ["outcome1", "outcome2"],
                    "reasoning": "explanation"
                }},
                "domain_mastery_score": {{
                    "score": 0-10,
                    "mastery_areas": ["area1", "area2"],
                    "gaps": ["area1", "area2"],
                    "reasoning": "explanation"
                }},
                "leadership_score": {{
                    "score": 0-10,
                    "leadership_evidence": ["evidence1", "evidence2"],
                    "reasoning": "explanation"
                }},
                "overall_elite_score": {{
                    "score": 0-10,
                    "strengths": ["strength1", "strength2"],
                    "concerns": ["concern1", "concern2"],
                    "recommendation": "submit|reject|consider"
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            logger.info(f"GPT-4 elite evaluation completed")
            return evaluation
            
        except Exception as e:
            logger.error(f"GPT-4 elite evaluation failed: {e}")
            return self._evaluate_against_smart_criteria_fallback(resume_text, smart_criteria)

    def _adjust_weights_dynamically_with_gpt4(self, context: Dict[str, Any], smart_criteria: Dict[str, Any]) -> Dict[str, float]:
        """
        Use GPT-4 to dynamically adjust weights based on context and smart criteria
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback weight adjustment")
            return self._adjust_weights_for_collateral(self.default_weights, "")
        
        try:
            prompt = f"""
            Based on the context and smart criteria, adjust the scoring weights for the FitScore evaluation.
            
            Context: {json.dumps(context, indent=2)}
            Smart Criteria: {json.dumps(smart_criteria, indent=2)}
            
            Current default weights:
            - Education: 20%
            - Career Trajectory: 20%
            - Company Relevance: 15%
            - Tenure Stability: 15%
            - Most Important Skills: 20%
            - Bonus Signals: 5%
            - Red Flags: -15% (penalty)
            
            Adjust weights based on:
            1. Industry requirements
            2. Company type (startup vs enterprise)
            3. Role level and complexity
            4. Growth stage and company size
            5. Specific role requirements
            
            Return adjusted weights in JSON:
            {{
                "education": 0.XX,
                "career_trajectory": 0.XX,
                "company_relevance": 0.XX,
                "tenure_stability": 0.XX,
                "most_important_skills": 0.XX,
                "bonus_signals": 0.XX,
                "red_flags": -0.XX,
                "reasoning": "explanation of adjustments"
            }}
            
            Ensure weights sum to 1.0 (excluding red_flags penalty).
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            adjusted_weights = json.loads(response.choices[0].message.content)
            logger.info(f"GPT-4 adjusted weights: {adjusted_weights}")
            return adjusted_weights
            
        except Exception as e:
            logger.error(f"GPT-4 weight adjustment failed: {e}")
            return self._adjust_weights_for_collateral(self.default_weights, "")

    # Fallback methods for when GPT-4 is not available
    def _detect_context_fallback(self, job_description: str) -> Dict[str, Any]:
        """Fallback context detection using pattern matching"""
        jd_lower = job_description.lower()
        
        # Detect industry
        industry = "general"
        if any(word in jd_lower for word in ["software", "engineer", "developer", "tech"]):
            industry = "tech"
        elif any(word in jd_lower for word in ["healthcare", "medical", "hospital", "clinic"]):
            industry = "healthcare"
        elif any(word in jd_lower for word in ["law", "legal", "attorney", "lawyer"]):
            industry = "law"
        elif any(word in jd_lower for word in ["accounting", "cpa", "audit", "finance"]):
            industry = "finance"
        
        # Detect company type
        company_type = "general"
        if any(word in jd_lower for word in ["startup", "seed", "series", "early-stage"]):
            company_type = "startup"
        elif any(word in jd_lower for word in ["enterprise", "fortune", "large company"]):
            company_type = "enterprise"
        elif any(word in jd_lower for word in ["law firm", "llp", "amlaw"]):
            company_type = "law_firm"
        elif any(word in jd_lower for word in ["accounting firm", "big 4"]):
            company_type = "accounting"
        elif any(word in jd_lower for word in ["hospital", "healthcare system"]):
            company_type = "healthcare"
        
        return {
            "industry": industry,
            "company_type": company_type,
            "role_type": self._detect_role_type(job_description),
            "role_level": "mid",  # Default
            "key_requirements": [],
            "preferences": [],
            "company_size": "medium",
            "growth_stage": "established"
        }

    def _generate_smart_criteria_fallback(self, job_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback smart criteria generation"""
        return {
            "mission_critical_skills": [],
            "elite_company_benchmarks": [],
            "expected_outcomes": [],
            "domain_mastery_requirements": [],
            "leadership_indicators": [],
            "technical_complexity": "medium",
            "scale_requirements": "medium",
            "industry_specific_requirements": []
        }

    def _extract_skills_fallback(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Fallback skills extraction using existing methods"""
        required_skills = self._extract_required_skills(job_description)
        candidate_skills = self._extract_candidate_skills(resume_text)
        
        return {
            "candidate_skills": [{"skill": skill, "evidence": "resume", "proficiency": "unknown", "years_experience": "unknown"} for skill in candidate_skills],
            "required_skills": [{"skill": skill, "importance": "required", "description": ""} for skill in required_skills],
            "skill_matches": [],
            "missing_critical_skills": [],
            "inferred_skills": []
        }

    def _evaluate_against_smart_criteria_fallback(self, resume_text: str, smart_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback evaluation using existing scoring methods"""
        return {
            "mission_critical_skills_score": {"score": 5.0, "matches": [], "gaps": [], "reasoning": "Fallback evaluation"},
            "elite_company_benchmark_score": {"score": 5.0, "company_matches": [], "reasoning": "Fallback evaluation"},
            "expected_outcomes_score": {"score": 5.0, "outcomes_demonstrated": [], "missing_outcomes": [], "reasoning": "Fallback evaluation"},
            "domain_mastery_score": {"score": 5.0, "mastery_areas": [], "gaps": [], "reasoning": "Fallback evaluation"},
            "leadership_score": {"score": 5.0, "leadership_evidence": [], "reasoning": "Fallback evaluation"},
            "overall_elite_score": {"score": 5.0, "strengths": [], "concerns": [], "recommendation": "consider"}
        }


# Example usage and testing
def main():
    """Example usage of the FitScore calculator"""
    
    # Initialize calculator
    calculator = FitScoreCalculator()
    
    # Sample resume and job description
    sample_resume = """
    John Doe
    Software Engineer
    
    EDUCATION:
    Massachusetts Institute of Technology
    Bachelor of Science in Computer Science
    GPA: 3.8
    
    EXPERIENCE:
    Senior Software Engineer
    Google Inc.
    2020-2023 (3 years)
    - Led team of 10 engineers
    - Built scalable microservices
    - Used Python, React, AWS, Docker
    
    Software Engineer
    Microsoft Corporation
    2018-2020 (2 years)
    - Developed web applications
    - Used JavaScript, Node.js, SQL
    
    SKILLS:
    Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, SQL, MongoDB
    
    BONUS:
    - Open source contributor
    - Published technical articles
    - Speaking at conferences
    """
    
    sample_job_description = """
    Senior Software Engineer
    Tech Startup
    
    We are looking for a Senior Software Engineer to join our growing team.
    
    Requirements:
    - 5+ years of software engineering experience
    - Strong knowledge of Python, JavaScript, React
    - Experience with AWS, Docker, Kubernetes
    - Experience with microservices architecture
    - Leadership experience preferred
    
    Nice to have:
    - Machine learning experience
    - Open source contributions
    - Startup experience
    """
    
    # Calculate fitscore
    result = calculator.calculate_fitscore(
        resume_text=sample_resume,
        job_description=sample_job_description,
        collateral="Startup environment with fast-paced culture and emphasis on technical skills."
    )
    
    # Print results
    print("=== FITSCORE CALCULATION RESULTS ===")
    print(f"Total Score: {result.total_score:.2f}")
    print(f"Submittable: {result.total_score >= 8.2}")
    print(f"\nCategory Scores:")
    print(f"Education: {result.education_score:.2f}")
    print(f"Career Trajectory: {result.career_trajectory_score:.2f}")
    print(f"Company Relevance: {result.company_relevance_score:.2f}")
    print(f"Tenure Stability: {result.tenure_stability_score:.2f}")
    print(f"Most Important Skills: {result.most_important_skills_score:.2f}")
    print(f"Bonus Signals: {result.bonus_signals_score:.2f}")
    print(f"Red Flags Penalty: {result.red_flags_penalty:.2f}")
    
    print(f"\nRecommendations:")
    for rec in result.recommendations:
        print(f"- {rec}")
    
    print(f"\nDetailed Results (JSON):")
    print(calculator.to_json(result))


def test_fitscore():
    """Quick test function to verify the calculator works"""
    calculator = FitScoreCalculator()
    
    # Simple test case
    resume = "Software Engineer at Google with Python, React, AWS experience. MIT graduate."
    jd = "Looking for Python developer with React and AWS experience."
    
    result = calculator.calculate_fitscore(resume, jd)
    
    print(f"Test Result: {result.total_score:.2f}")
    print(f"Submittable: {result.total_score >= 8.2}")
    return result


if __name__ == "__main__":
    main() 

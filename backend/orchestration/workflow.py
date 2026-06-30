import asyncio
import json
import traceback
from backend.db.db_manager import (
    update_project_status, 
    add_project_log, 
    save_blueprint_artifact, 
    save_project_summary
)

# Import the specialized agents
from backend.agents.planner import PlannerAgent
from backend.agents.idea_gen import IdeaGenerationAgent
from backend.agents.research import ResearchAgent
from backend.agents.dataset import DatasetDiscoveryAgent
from backend.agents.tech_advisor import TechnologyAdvisorAgent
from backend.agents.architecture import SystemArchitectureAgent
from backend.agents.dev_planner import DevelopmentPlannerAgent
from backend.agents.readme_gen import ReadmeGeneratorAgent
from backend.agents.pitch_gen import PitchGeneratorAgent
from backend.agents.reviewer import SubmissionReviewAgent
from backend.agents.pm import ProjectManagerAgent

async def run_workflow(project_id: str, name: str, theme: str, problem_statement: str, constraints: str, tech_preferences: str, api_key: str = None):
    try:
        update_project_status(project_id, "RUNNING")
        add_project_log(project_id, "System", "Initializing Multi-Agent Orchestrator...")
        
        # Instantiate agents
        planner = PlannerAgent()
        idea_gen = IdeaGenerationAgent()
        research_client = ResearchAgent()
        dataset_discoverer = DatasetDiscoveryAgent()
        tech_advisor = TechnologyAdvisorAgent()
        system_arch = SystemArchitectureAgent()
        dev_planner = DevelopmentPlannerAgent()
        readme_generator = ReadmeGeneratorAgent()
        pitch_generator = PitchGeneratorAgent()
        submission_reviewer = SubmissionReviewAgent()
        project_manager = ProjectManagerAgent()

        # Step 1: Planner Agent coordinates the request
        add_project_log(project_id, "System", "Step 1: Planner Agent starting...")
        planner_out = await asyncio.to_thread(
            planner.execute, project_id, name, theme, problem_statement, constraints, tech_preferences, api_key
        )
        save_blueprint_artifact(project_id, "Planner Analysis", planner_out.analysis)
        
        # Step 2: Idea Gen and Research run in parallel
        add_project_log(project_id, "System", "Step 2: Starting Idea Gen and Research Agents in parallel...")
        
        async def run_idea_gen():
            return await asyncio.to_thread(
                idea_gen.execute, project_id, name, theme, problem_statement, constraints, tech_preferences, api_key
            )
            
        async def run_research():
            return await asyncio.to_thread(
                research_client.execute, project_id, problem_statement, theme, api_key
            )
            
        idea_out, research_out = await asyncio.gather(run_idea_gen(), run_research())
        
        # Save results of Step 2
        # Format ideas output
        ideas_md = f"### Selected Best Idea: {idea_out.best_idea_name}\n\n"
        ideas_md += f"**Reasoning:** {idea_out.selection_reasoning}\n\n"
        ideas_md += "#### Brainstormed Candidates:\n"
        for idx, idea in enumerate(idea_out.ideas, 1):
            ideas_md += f"{idx}. **{idea.name}** - *{idea.tagline}*\n"
            ideas_md += f"   - Description: {idea.description}\n"
            ideas_md += f"   - Innovation: {idea.innovation_score}/10 | Feasibility: {idea.feasibility_score}/10\n"
            ideas_md += f"   - Rationale: {idea.reasoning}\n\n"
        save_blueprint_artifact(project_id, "Project Ideas", ideas_md)
        
        # Format research output
        competitors_md = "#### Competitor Analysis Matrix:\n\n"
        for comp in research_out.similar_projects:
            competitors_md += f"• **{comp.name}** ({comp.url or 'N/A'})\n"
            competitors_md += f"  *Description:* {comp.description}\n"
            competitors_md += f"  *Key Features:* {', '.join(comp.features)}\n\n"
            
        save_blueprint_artifact(project_id, "Research Summary", research_out.research_summary)
        save_blueprint_artifact(project_id, "Competitor Analysis", competitors_md)
        save_blueprint_artifact(project_id, "Existing Solutions & Gaps", f"**Existing Solutions:**\n{research_out.existing_solutions}\n\n**Gaps:**\n" + "\n".join(f"- {gap}" for gap in research_out.innovation_gaps))

        # Step 3: Dataset Discovery, Tech Advisor, and Pitch Generator run in parallel
        add_project_log(project_id, "System", "Step 3: Starting Dataset Discovery, Tech Advisor, and Pitch Generator in parallel...")
        
        selected_idea_name = idea_out.best_idea_name
        selected_idea_desc = next((i.description for i in idea_out.ideas if i.name == selected_idea_name), problem_statement)
        innovation_gaps_str = "\n".join(research_out.innovation_gaps)
        
        async def run_datasets():
            return await asyncio.to_thread(
                dataset_discoverer.execute, project_id, selected_idea_name, selected_idea_desc, api_key
            )
            
        async def run_tech():
            return await asyncio.to_thread(
                tech_advisor.execute, project_id, selected_idea_name, selected_idea_desc, constraints, tech_preferences, api_key
            )
            
        async def run_pitch():
            return await asyncio.to_thread(
                pitch_generator.execute, project_id, selected_idea_name, selected_idea_desc, innovation_gaps_str, api_key
            )
            
        dataset_out, tech_out, pitch_out = await asyncio.gather(run_datasets(), run_tech(), run_pitch())
        
        # Save results of Step 3
        # Format Datasets
        datasets_md = "#### Recommmended Public Datasets:\n"
        for ds in dataset_out.datasets:
            datasets_md += f"• **{ds.name}** (Source: {ds.source})\n"
            datasets_md += f"  *Description:* {ds.description}\n"
            datasets_md += f"  *Usefulness:* {ds.usefulness}\n"
            datasets_md += f"  *Link:* [{ds.recommended_url}]({ds.recommended_url})\n\n"
        datasets_md += "\n#### Alternative APIs & Sources:\n"
        for api_item in dataset_out.alternative_apis:
            datasets_md += f"• **{api_item.name}** (Provider: {api_item.provider})\n"
            datasets_md += f"  *Purpose:* {api_item.purpose}\n"
            datasets_md += f"  *Usefulness:* {api_item.usefulness}\n\n"
        save_blueprint_artifact(project_id, "Datasets & APIs", datasets_md)
        
        # Format Tech Stack
        tech_md = f"#### Tech Stack Summary:\n{tech_out.summary_rationale}\n\n"
        tech_md += f"• **Frontend:** {tech_out.frontend.technology}\n  *Rationale:* {tech_out.frontend.explanation}\n\n"
        tech_md += f"• **Backend:** {tech_out.backend.technology}\n  *Rationale:* {tech_out.backend.explanation}\n\n"
        tech_md += f"• **Database:** {tech_out.database.technology}\n  *Rationale:* {tech_out.database.explanation}\n\n"
        tech_md += f"• **AI/ML Stack:** {tech_out.ai_framework.technology}\n  *Rationale:* {tech_out.ai_framework.explanation}\n\n"
        tech_md += f"• **Cloud/Hosting:** {tech_out.cloud_platform.technology}\n  *Rationale:* {tech_out.cloud_platform.explanation}\n\n"
        tech_md += "#### Secondary Tools & Utility APIs:\n"
        for s_api in tech_out.apis:
            tech_md += f"- **{s_api.technology}**: {s_api.explanation}\n"
        save_blueprint_artifact(project_id, "Technology Stack", tech_md)
        
        # Format Pitch
        pitch_md = f"### Elevator Pitch\n> {pitch_out.elevator_pitch}\n\n"
        pitch_md += "### Presentation Slides Outline\n"
        for s in pitch_out.presentation_outline:
            pitch_md += f"#### Slide {s.slide_number}: {s.title}\n"
            pitch_md += "  **Bullet Points:**\n"
            for bp in s.bullet_points:
                pitch_md += f"  - {bp}\n"
            pitch_md += f"  **Visual suggestion:** *{s.visual_suggestion}*\n\n"
            
        demo_md = "#### Interactive Demo Video Script:\n"
        for step in pitch_out.demo_flow:
            demo_md += f"- {step}\n"
            
        future_scope_md = "#### Future Growth & Scalability:\n"
        for fs in pitch_out.future_scope:
            future_scope_md += f"- {fs}\n"
            
        save_blueprint_artifact(project_id, "Pitch Deck Outline", pitch_md)
        save_blueprint_artifact(project_id, "Demo Script", demo_md)
        save_blueprint_artifact(project_id, "Future Scope", future_scope_md)
        
        # Step 4: System Architecture and Development Planner run in parallel (since tech stack is ready)
        add_project_log(project_id, "System", "Step 4: Starting System Architecture and Development Planner in parallel...")
        tech_stack_summary = f"Frontend: {tech_out.frontend.technology}, Backend: {tech_out.backend.technology}, DB: {tech_out.database.technology}, AI: {tech_out.ai_framework.technology}"
        
        async def run_arch():
            return await asyncio.to_thread(
                system_arch.execute, project_id, selected_idea_name, selected_idea_desc, tech_stack_summary, api_key
            )
            
        async def run_dev_planner():
            return await asyncio.to_thread(
                dev_planner.execute, project_id, selected_idea_name, selected_idea_desc, tech_stack_summary, api_key
            )
            
        arch_out, dev_out = await asyncio.gather(run_arch(), run_dev_planner())
        
        # Save results of Step 4
        # Format Architecture
        arch_md = f"#### Architecture Overview:\n{arch_out.architecture_overview}\n\n"
        arch_md += f"```mermaid\n{arch_out.mermaid_diagram}\n```\n\n"
        arch_md += f"#### Data Flow Path:\n{arch_out.data_flow_explanation}\n\n"
        arch_md += f"#### AI Model Orchestration Flow:\n{arch_out.ai_workflow_explanation}\n"
        save_blueprint_artifact(project_id, "System Architecture", arch_md)
        
        # Format Dev Roadmap
        roadmap_md = f"#### Project Complexity: **{dev_out.complexity_estimation}**\n\n"
        roadmap_md += f"#### Core Feature MVP Matrix:\n{dev_out.prioritization_matrix}\n\n"
        roadmap_md += f"#### Execution Roadmap Summary:\n{dev_out.roadmap_summary}\n\n"
        roadmap_md += "#### Detailed Milestone Phases:\n"
        for m in dev_out.milestones:
            roadmap_md += f"• **{m.title}** (Estimated: {m.estimated_hours} hours)\n"
            roadmap_md += f"  *Overview:* {m.description}\n"
            roadmap_md += "  *Tasks:* \n"
            for t in m.tasks:
                roadmap_md += f"    - {t}\n"
            roadmap_md += "\n"
        save_blueprint_artifact(project_id, "Development Roadmap", roadmap_md)
        
        # Step 5: README Gen and Submission Review run in parallel
        add_project_log(project_id, "System", "Step 5: Starting README Generator and Submission Review in parallel...")
        
        # Context strings for later stages
        compiled_artifacts_str = (
            f"# Selected Idea:\n{ideas_md}\n\n"
            f"# Competitors & Gaps:\n{competitors_md}\n\n"
            f"# Tech Recommendations:\n{tech_md}\n\n"
            f"# Architecture & Data Flow:\n{arch_md}\n\n"
            f"# Development Roadmap:\n{roadmap_md}\n\n"
            f"# Pitch Presentation:\n{pitch_md}\n"
        )
        
        async def run_readme():
            return await asyncio.to_thread(
                readme_generator.execute, project_id, selected_idea_name, selected_idea_desc, tech_stack_summary, arch_out.architecture_overview, api_key
            )
            
        async def run_reviewer():
            return await asyncio.to_thread(
                submission_reviewer.execute, project_id, compiled_artifacts_str, api_key
            )
            
        readme_out, review_out = await asyncio.gather(run_readme(), run_reviewer())
        
        # Save results of Step 5
        save_blueprint_artifact(project_id, "README", readme_out.readme_content)
        
        # Format Reviewer Results
        review_md = f"#### Architectural Consistency Check:\n{review_out.consistency_check}\n\n"
        review_md += "#### Identified Gaps & Missing Information:\n"
        for ms in review_out.missing_sections:
            review_md += f"- {ms}\n"
        review_md += "\n#### Recommended Quality Improvements:\n"
        for imp in review_out.improvement_suggestions:
            review_md += f"- {imp}\n"
        save_blueprint_artifact(project_id, "Reviewer Audit", review_md)
        
        checklist_md = "#### Ultimate Submission Checklist:\n"
        for item in review_out.submission_checklist:
            checklist_md += f"- [ ] {item}\n"
        save_blueprint_artifact(project_id, "Submission Checklist", checklist_md)
        
        # Step 6: Project Manager compiles final executive summary and blueprint
        add_project_log(project_id, "System", "Step 6: Project Manager compiling final unified blueprint...")
        reviewer_text_summary = f"{review_out.consistency_check}\nMissing sections: {', '.join(review_out.missing_sections)}\nSuggestions: {', '.join(review_out.improvement_suggestions)}"
        
        pm_out = await asyncio.to_thread(
            project_manager.execute, project_id, compiled_artifacts_str, reviewer_text_summary, api_key
        )
        
        save_project_summary(project_id, pm_out.executive_summary)
        save_blueprint_artifact(project_id, "Executive Summary", pm_out.executive_summary)
        save_blueprint_artifact(project_id, "Polished Blueprint", pm_out.polished_blueprint)
        
        add_project_log(project_id, "System", "Hackathon Project Blueprint forged successfully!")
        update_project_status(project_id, "COMPLETED")
        
    except Exception as e:
        err = f"Workflow orchestration failed: {str(e)}\n{traceback.format_exc()}"
        add_project_log(project_id, "System", f"FATAL ERROR: {err}")
        update_project_status(project_id, "FAILED")
        print(err)

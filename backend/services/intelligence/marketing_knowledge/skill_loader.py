"""
Skill Loader
============
Reads raw `.md` Playbook files and extracts out structured components like
'Frameworks', 'Steps', and 'Outputs' into python `SkillObjects`.
"""

import os
import re
import logging
from typing import Dict, List, Optional

from .models import SkillObject

logger = logging.getLogger(__name__)

class SkillLoader:
    """Parses markdown playbooks into structured AI memory objects."""

    def __init__(self, playbooks_dir: Optional[str] = None):
        """Initializes with the path to the stored playbooks."""
        if not playbooks_dir:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.playbooks_dir = os.path.join(base_dir, "marketing_playbooks")
        else:
            self.playbooks_dir = playbooks_dir
            
    def load_all_skills(self) -> Dict[str, SkillObject]:
        """Loads all available playbooks in the directory."""
        skills = {}
        if not os.path.exists(self.playbooks_dir):
            logger.warning(f"Playbooks directory not found at {self.playbooks_dir}")
            return skills

        logger.info(f"[SkillLoader] Scanning {self.playbooks_dir} for AI playbooks.")

        for filename in os.listdir(self.playbooks_dir):
            if filename.endswith(".md"):
                skill_name = filename.replace(".md", "")
                filepath = os.path.join(self.playbooks_dir, filename)
                
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        raw_content = f.read()
                        
                    parsed_skill = self._parse_markdown(skill_name, raw_content)
                    skills[skill_name] = parsed_skill
                    logger.debug(f"[SkillLoader] Loaded {skill_name} successfully.")
                    
                except Exception as e:
                    logger.error(f"[SkillLoader] Failed to parse {filename}: {e}")

        return skills

    def _parse_markdown(self, skill_name: str, content: str) -> SkillObject:
        """
        Extracts structural blocks using naive regex splitting.
        Looks for '#' headers to bucket knowledge.
        """
        lines = content.split('\n')
        title = skill_name.replace("_", " ").title()
        description = []
        instructions = []
        examples = []
        
        current_section = "intro"
        
        for line in lines:
            if line.startswith("# "):
                title = line.replace("# ", "").strip()
                continue
            elif line.startswith("## Steps") or line.startswith("## The Framework"):
                current_section = "steps"
                continue
            elif "Output" in line and line.startswith("##"):
                current_section = "outputs"
                continue
            elif "Frameworks" in line and line.startswith("##"):
                current_section = "frameworks"
                continue
                
            if line.strip() == "":
                 continue
                 
            # Bucket the text
            if current_section == "intro":
                description.append(line.strip())
            elif current_section == "steps":
                instructions.append(line.strip())
            elif current_section in ("frameworks", "outputs"):
                 # We loosely bucket examples vs outputs depending on the playbook format
                 examples.append(line.strip())

        return SkillObject(
            name=skill_name,
            title=title,
            description=" ".join(description) if description else "Loaded from markdown.",
            instructions=instructions,
            examples=examples,
            raw_markdown=content
        )
